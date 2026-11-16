"""Real model evaluation; results are observations, automatic scores are provisional."""
import argparse
import json
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import ROOT, OLLAMA_BASE_URL
from rag import build_index, answer_question, OllamaClient, RagError


class RecordingClient(OllamaClient):
    last_output = None

    def generate(self, question, retrieved):
        self.last_output = super().generate(question, retrieved)
        return self.last_output


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default=OLLAMA_BASE_URL)
    parser.add_argument('--cases', type=Path, default=ROOT / 'test_cases.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'output' / 'evaluation.json')
    parser.add_argument('--limit', type=int, default=0)
    args = parser.parse_args()
    cases = json.loads(args.cases.read_text(encoding='utf-8'))
    if args.limit:
        cases = cases[:args.limit]
    folder = ROOT / 'output'
    folder.mkdir(exist_ok=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    results = []
    try:
        client = RecordingClient(args.url)
        index = build_index((ROOT / 'knowledge_base.json').read_text(encoding='utf-8'), args.url)
        for case in cases:
            start = time.perf_counter()
            try:
                answer = answer_question(case['question'], index, client).to_dict()
                retrieved = [r['entry']['id'] for r in answer['retrieved_entries']]
                retrieval_ok = set(case['expected_ids']) <= set(retrieved)
                passed = (answer['status'] == 'answered' and all(k.casefold() in answer['answer'].casefold() for k in case['keywords'])) if case['expected_answerable'] else answer['status'] == 'unknown'
                result = {**case, **answer, 'model_output': client.last_output, 'retrieved_ids': retrieved, 'passed_automatic': passed,
                          'failure_stage': '' if passed else ('retrieval' if not retrieval_ok else 'generation')}
            except RagError as exc:
                result = {**case, 'error': str(exc), 'passed_automatic': False, 'failure_stage': 'connection'}
            result['seconds'] = round(time.perf_counter()-start, 2)
            results.append(result)
            print(case['id'], result['passed_automatic'], result['seconds'], flush=True)
            args.output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    except RagError as exc:
        print(str(exc))
        return 1
    print('Kết quả lưu trong', args.output, '. Cần người đọc duyệt độ đúng và căn cứ nguồn.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
