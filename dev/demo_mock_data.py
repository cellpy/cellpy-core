import matplotlib.pyplot as plt
from cellpycore._helpers import create_raw_data


def main():
    df = create_raw_data()
    print(df)

    plt.plot(df["test_time"], df["potential"])
    plt.show()


if __name__ == "__main__":
    main()
