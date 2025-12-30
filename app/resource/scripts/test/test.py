import time
import argparse


def main():
    parser = argparse.ArgumentParser(description="打印测试脚本")
    parser.add_argument("--count", type=int, default=5, help="打印次数")
    parser.add_argument("--delay", type=float, default=1.0, help="每次打印间隔秒数")
    args = parser.parse_args()

    for i in range(args.count):
        print(f"[{i+1}] Hello World")
        time.sleep(args.delay)


if __name__ == "__main__":
    main()
