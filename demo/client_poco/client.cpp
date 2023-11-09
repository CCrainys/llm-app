#include "spdlog/spdlog.h"
#include <Poco/Exception.h>
#include <Poco/JSON/Parser.h>
#include <Poco/Net/HTTPClientSession.h>
#include <Poco/Net/HTTPRequest.h>
#include <Poco/Net/HTTPResponse.h>
#include <Poco/Path.h>
#include <Poco/StreamCopier.h>
#include <Poco/URI.h>
#include <chrono>
#include <future>
#include <iostream>
#include <string>
#include <thread>

void get_answer(std::string prompt,
                std::promise<std::tuple<std::string, double, double>> prom) {
    try {
        auto start = std::chrono::high_resolution_clock::now();
        Poco::URI uri("http://localhost:8080/");
        uri.addQueryParameter("prompt", prompt);
        auto path(uri.getPathAndQuery());
        if (path.empty()) {
            path = "/";
        }

        Poco::Net::HTTPClientSession session(uri.getHost(), uri.getPort());
        Poco::Net::HTTPRequest req(Poco::Net::HTTPRequest::HTTP_GET, path,
                                   Poco::Net::HTTPMessage::HTTP_1_1);

        std::ostream &ostr = session.sendRequest(req);
        ostr << prompt;

        Poco::Net::HTTPResponse res;
        std::istream &rs = session.receiveResponse(res);

        std::string result;
        Poco::StreamCopier::copyToString(rs, result);
        auto parsed_object = Poco::JSON::Parser().parse(result).extract<Poco::JSON::Object::Ptr>();
        auto answer = parsed_object->getValue<std::string>("answer");
        auto inference_time_str = parsed_object->getValue<std::string>("inference_time");
        auto inference_time = std::stod(inference_time_str);

        auto end = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double> diff = end - start;
        auto request_time = diff.count();
        prom.set_value({answer, inference_time, request_time});
    } catch (Poco::Exception &ex) {
        std::cerr << ex.displayText() << std::endl;
        prom.set_value({"error", 0, 0});
    }
}

int main() {
    std::vector<std::thread> threads;

    std::vector<int> num_threads = {1, 2, 4, 8, 16, 32, 64, 128, 256};
    for (auto thread : num_threads) {
        threads.resize(thread);

        double total_inference_time = 0;
        double total_request_time = 0;

        // FIXME: conditional compilation doesn't work here
        spdlog::set_level(spdlog::level::info);

        for (int i = 0; i < thread; i++) {
            auto prompt = std::string("What is USTC?");
            std::promise<std::tuple<std::string, double, double>> prom;
            auto fut = prom.get_future();
            threads[i] = std::thread(get_answer, std::move(prompt), std::move(prom));
            auto [answer, inference_time, request_time] = fut.get();
            if (answer == "error") {
                std::cout << "error" << std::endl;
                continue;
            }

            spdlog::debug("result: {}", answer);
            spdlog::debug("inference_time: {:<10.8f}", inference_time);
            spdlog::debug("request_time: {:<10.8f}", request_time);

            total_inference_time += inference_time;
            total_request_time += request_time;
        }

        for (std::thread &thread : threads) {
            thread.join();
        }

        spdlog::info("number of threads:{}", thread);
        spdlog::info("average inference time: {:<10.8f}", total_inference_time / static_cast<double>(thread));
        spdlog::info("average request time: {:<10.8f}", total_request_time / static_cast<double>(thread));
    }

    return 0;
}
