with open("./gpu_usage.txt", "r") as f:
    lines = f.readlines()
    gpu_usage = [int(line.strip()) for line in lines]
    print("Average GPU utilization: ", sum(gpu_usage) / len(gpu_usage))
    print("Max GPU utilization: ", max(gpu_usage))
    print("Min GPU utilization: ", min(gpu_usage))
