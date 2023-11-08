#include "spdlog/spdlog.h"
#include <Poco/Exception.h>
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
                std::promise<std::pair<std::string, double>> prom) {
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
        std::string answer;
        Poco::StreamCopier::copyToString(rs, answer);

        auto end = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double> diff = end - start;
        auto request_time = diff.count();
        prom.set_value({answer, request_time});
    } catch (Poco::Exception &ex) {
        std::cerr << ex.displayText() << std::endl;
        prom.set_value({"error", 0});
    }
}

int main() {
    std::vector<std::thread> threads;
    std::vector<std::string> prompts = {"What is Task Decomposition?",
                                        "What is AI?", "What is Python?",
                                        "What is C++?"};

    std::vector<int> repeat_times = {1, 2, 4, 8, 16, 32, 64};
    for (auto repeats : repeat_times) {
        threads.resize(prompts.size() * repeats);

        double total_inference_time = 0;
        double total_request_time = 0;

        auto index = 0;

        // FIXME: conditional compilation doesn't work here
        spdlog::set_level(spdlog::level::info);

        for (int i = 0; i < repeats; i++) {
            for (auto &prompt : prompts) {
                std::promise<std::pair<std::string, double>> prom;
                auto fut = prom.get_future();
                threads[index] = std::thread(get_answer, std::move(prompt), std::move(prom));
                auto [result, request_time] = fut.get();
                if (result == "error") {
                    std::cout << "error" << std::endl;
                    continue;
                }
                auto len = result.size();
                auto answer = result.substr(0, len - 10);
                auto inference_time = result.substr(len - 10, 10);
                spdlog::debug("result: {}", answer);
                spdlog::debug("inference_time: {}", inference_time);
                spdlog::debug("request_time: {}", request_time);

                total_inference_time += std::stod(inference_time);
                total_request_time += request_time;
                index++;
            }
        }

        for (std::thread &thread : threads) {
            thread.join();
        }

        spdlog::info("number of threads:{}", index);
        spdlog::info("average inference time: {:<10.8f}", total_inference_time / static_cast<double>(index));
        spdlog::info("total request time: {:<10.8f}", total_request_time / static_cast<double>(index));
    }

    return 0;
}
