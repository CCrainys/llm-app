CXX := g++
TARGET := client
CXXFLAGS := -std=c++17 -Wall -Wextra -Werror -pthread
LDLIBS := -lPocoNet -lPocoFoundation

all: $(TARGET)

$TARGET:
	$(CXX) $(CXXFLAGS) -o $@ $@.cpp $(LDLIBS)
