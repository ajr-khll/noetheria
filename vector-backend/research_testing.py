import deep_research
import vector_store_modification


vector_store_modification.collect_and_process_files()



for chunk in deep_research.run_deep_research("Give me 500 words on Nietzsche and his connection to fascism.", deep_research.assistant_id):
    print(chunk, end="", flush=True)

