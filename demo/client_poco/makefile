CXX := g++
TARGET := client
CXXFLAGS := -std=c++17 -Wall -Wextra -Werror -pthread
LDLIBS := -lPocoNet -lPocoJSON -lPocoFoundation

all: $(TARGET)

debug: CXXFLAGS += -DSPDLOG_ACTIVE_LEVEL=SPDLOG_LEVEL_DEBUG
debug: $(TARGET)

.PHONY clean:
	rm -f $(TARGET)

$TARGET:
	$(CXX) $(CXXFLAGS) -o $@ $@.cpp $(LDLIBS)
