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

// Have to be global to avoid copying in the thread
std::vector<std::string> prompts = {"What is Task Decomposition?",
                                    "What is AI?", "What is Python?",
                                    "What is C++?"};

void get_answer(int thread_id,
                std::promise<std::tuple<double, double>> prom) {
    spdlog::debug("thread_id: {}", thread_id);
    double total_inference_time = 0;
    double total_request_time = 0;

    std::vector<std::future<std::tuple<double, double>>> futures;
    for (auto &prompt : prompts) {
        futures.push_back(std::async(std::launch::async, [&]() -> std::tuple<double, double> {
            double inference_time = 0;
            double request_time = 0;
            try {
                auto start = std::chrono::high_resolution_clock::now();

                Poco::URI uri("http://localhost:8080/");
                Poco::Net::HTTPClientSession session(uri.getHost(), uri.getPort());
                uri.addQueryParameter("prompt", prompt);
                auto path(uri.getPathAndQuery());

                Poco::Net::HTTPRequest req(Poco::Net::HTTPRequest::HTTP_GET, path,
                                           Poco::Net::HTTPMessage::HTTP_1_1);

                session.sendRequest(req);

                Poco::Net::HTTPResponse res;
                std::istream &rs = session.receiveResponse(res);

                std::string result;
                Poco::StreamCopier::copyToString(rs, result);
                auto parsed_object = Poco::JSON::Parser().parse(result).extract<Poco::JSON::Object::Ptr>();
                auto answer = parsed_object->getValue<std::string>("answer");
                auto inference_time_str = parsed_object->getValue<std::string>("inference_time");
                inference_time = std::stod(inference_time_str);

                auto end = std::chrono::high_resolution_clock::now();
                std::chrono::duration<double> diff = end - start;
                request_time = diff.count();

                spdlog::debug("answer for: {} is {}", prompt, answer);
                spdlog::debug("inference_time: {:<10.8f}", inference_time);
                spdlog::debug("request_time: {:<10.8f}", request_time);
            } catch (Poco::Exception &ex) {
                spdlog::debug("error: {}", ex.displayText());
            }
            return {inference_time, request_time};
        }));
    }

    for (auto &future : futures) {
        auto [inference_time, request_time] = future.get();
        total_inference_time += inference_time;
        total_request_time += request_time;
    }

    prom.set_value({total_inference_time, total_request_time});
}

int main() {
    std::vector<std::thread> threads;

    std::vector<int> num_threads = {256};
    for (auto thread : num_threads) {
        threads.resize(thread);

        double total_inference_time = 0;
        double total_request_time = 0;

        // FIXME: conditional compilation doesn't work here
        spdlog::set_level(spdlog::level::debug);

        for (int i = 0; i < thread; i++) {
            std::promise<std::tuple<double, double>> prom;
            auto fut = prom.get_future();
            threads[i] = std::thread(get_answer, i, std::move(prom));
            auto [inference_time, request_time] = fut.get();

            total_inference_time += inference_time;
            total_request_time += request_time;
        }

        for (std::thread &thread : threads) {
            thread.join();
        }

        spdlog::info("number of threads: {}", thread);
        spdlog::info("average inference time: {:<10.8f}", total_inference_time / static_cast<double>(thread * prompts.size()));
        spdlog::info("average request time: {:<10.8f}", total_request_time / static_cast<double>(thread * prompts.size()));
    }

    return 0;
}
