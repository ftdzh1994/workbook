def main():
    from loguru import logger
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from document import load_json
    from tqdm import tqdm
    import pathlib, json
    import contextvars
    import uuid
    import sys

    # Define a ContextVar for tracking unique identifiers
    trace_id_var = contextvars.ContextVar('trace_id',default='0001')
    
    # 自定义 loguru 格式，包含 request_id
    def formatter(record):
        record["trace_id"] = trace_id_var.get()
        # return "{time:YYYY-MM-DD HH:mm:ss} ({file}:{line}) [{level}] |{trace_id}|: {message}\n"
        return "{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {module}:{function}:{line} |{trace_id}|: {message}\n"

    # Configure logger format to include trace_id
    logger.remove()  # Remove the default logger
    logger.add(
        "data/llm_dl.log",
        format=formatter,
    )

    # Initialize paths and extractor
    path = pathlib.Path("data")
    extractor = DLSG_Extractor(llm, "examples_db/common_examples_general.json")

    def process_file(json_path):
        # Generate a unique trace ID for this task
        trace_id = str(uuid.uuid4())
        trace_id_var.set(trace_id)

        logger.info(f'Processing file: {json_path.name}')
        json_data = load_json(json_path)
        result = extractor(json_data)
        result_path = path.joinpath("dl_result").joinpath(json_path.name)
        
        with open(result_path, "w") as fw:
            json.dump(result, fw, ensure_ascii=False)

        logger.info(f'Completed processing file: {json_path.name}')

    # Collect all file paths
    json_paths = list(path.joinpath("dl_ocr").glob("*.json"))
    idx2file = load_json('./data/dl_metadata.json')
    file2idx = {v:int(k) for k,v in idx2file.items()}
    json_paths = [f for f in json_paths if file2idx[(f.stem + '.txt')] <= 50]

    # Use ThreadPoolExecutor to process files in parallel
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_file, json_path) for json_path in json_paths]
        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing Progress"):
            try:
                future.result()
            except Exception as e:
                trace_id = trace_id_var.get()
                logger.error(f'Error processing file: {e}')