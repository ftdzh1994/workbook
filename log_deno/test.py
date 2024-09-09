import requests
import concurrent.futures
import time

def send_request(url):
    start_time = time.time()
    response = requests.get(url)
    end_time = time.time()
    return response.text, end_time - start_time

def main():
    url = "http://localhost:5000"
    num_requests = 1

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
        futures = [executor.submit(send_request, url) for _ in range(num_requests)]

        for future in concurrent.futures.as_completed(futures):
            result, elapsed_time = future.result()
            print(f"Response: {result}")
            print(f"Request took {elapsed_time:.2f} seconds")
            print("---")

if __name__ == "__main__":
    main()