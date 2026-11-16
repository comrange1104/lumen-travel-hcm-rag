"""Presentation typography and timed text, separate from the live demo controller."""
from html import escape
import re
import textwrap
import streamlit as st


def apply_style(active):
    st.markdown('''<style>
    .block-container{max-width:1240px;padding:2.5rem 3rem}
    .slide-heading{text-align:center;font-size:clamp(2rem,3.6vw,3rem);
      line-height:1.2;letter-spacing:-.035em;font-weight:750;margin:0 0 1.4rem;color:#203e31}
    .slide-copy{text-align:center;max-width:1000px;margin:1rem auto 1.8rem;
      font-size:clamp(1.55rem,2.7vw,2.35rem);line-height:1.5;font-weight:500;
      color:#263c30;text-wrap:balance;min-height:3em}
    .slide-body{text-align:center;max-width:1020px;margin:1rem auto;
      font-size:clamp(1.1rem,1.7vw,1.45rem);line-height:1.6;color:#425a4b;text-wrap:balance}
    .slide-answer{text-align:center;padding:1.1rem 1.8rem;border-radius:18px;
      background:#eaf2e9;color:#1d503b;font-size:clamp(1.45rem,2.2vw,1.9rem);
      line-height:1.5;margin:.7rem auto 1.5rem;max-width:1050px}
    .slide-eyebrow{text-align:center;letter-spacing:.17em;font-size:.85rem;
      font-weight:650;color:#738377;margin-bottom:1rem}
    .slide-brand{text-align:center;font-size:clamp(3.5rem,7vw,6rem);line-height:1.12;
      font-weight:800;letter-spacing:-.055em;color:#193f2c;margin:.4rem 0 1rem}
    .slide-subtitle{text-align:center;font-size:clamp(1.35rem,2.5vw,2rem);
      line-height:1.45;color:#3b5746;margin:0 auto 1rem;text-wrap:balance}
    .slide-author{text-align:center;font-size:1.2rem;color:#718071;margin:.8rem auto 1.5rem}
    .slide-footnote{text-align:center;color:#7a897d;font-size:.95rem;margin:1rem auto}
    .slide-cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1.2rem;
      max-width:1050px;margin:1.4rem auto}
    .slide-card{border:1px solid #d7e1d4;border-radius:20px;padding:1.6rem 1.8rem;background:#f0f4ed}
    .slide-card h3{font-size:1.5rem;margin:0 0 .7rem;color:#244331;text-align:left}
    .slide-card p{font-size:1.2rem;line-height:1.65;color:#47604e;margin:0;text-align:left}
    .source-chips{display:flex;justify-content:center;gap:.7rem;flex-wrap:wrap;margin:1rem auto}
    .source-chip{font-size:1rem;border:1px solid #d7e1d4;border-radius:12px;padding:.6rem .85rem;color:#4a6551}
    .source-excerpt{max-width:950px;margin:1rem auto;padding:1.3rem 1.6rem;border-left:4px solid #709378;background:#f0f4ed;border-radius:8px}
    .source-excerpt p{font-size:1.2rem;line-height:1.6;margin:.4rem 0}
    .source-excerpt a{color:#35644b;font-size:1rem}
    @media(max-width:700px){.slide-cards{grid-template-columns:1fr}}
    </style>''', unsafe_allow_html=True)
    if active:
        st.markdown('''<style>
        [data-testid="stHeader"], [data-testid="stToolbar"], footer{display:none!important}
        .block-container{min-height:100dvh;display:flex;flex-direction:column;
          justify-content:center;padding-top:2.2rem;padding-bottom:2.2rem}
        [data-testid="stTable"]{font-size:clamp(1rem,1.6vw,1.35rem)}
        [data-testid="stTable"] td,[data-testid="stTable"] th{padding:.7rem 1rem}
        [data-testid="stCode"] pre{font-size:clamp(.95rem,1.35vw,1.2rem)!important;line-height:1.55}
        [data-testid="stChatMessage"] p{font-size:clamp(1.25rem,2vw,1.7rem);text-align:center}
        [data-testid="stCaptionContainer"] p{text-align:center}
        [data-testid="stLinkButton"]{display:flex;justify-content:center}
        .st-key-record-controls{position:fixed;right:18px;bottom:14px;z-index:1000;
          width:auto!important;opacity:.12;transition:opacity .15s}
        .st-key-record-controls:hover,.st-key-record-controls:focus-within{opacity:1}
        .st-key-record-controls [data-testid="stPopover"]>button{min-width:36px;padding:.1rem .5rem}
        @media(max-width:800px){.block-container{padding:1.5rem}.slide-copy{font-size:1.55rem}}
        </style>''', unsafe_allow_html=True)


def heading(text):
    st.markdown(f'<h1 class="slide-heading">{escape(text)}</h1>', unsafe_allow_html=True)


def body(text, kind='body'):
    if kind not in ('body', 'answer', 'footnote'):
        raise ValueError('Unknown presentation text style')
    st.markdown(f'<div class="slide-{kind}">{escape(text)}</div>', unsafe_allow_html=True)


def speech_chunks(text):
    chunks = []
    for sentence in re.split(r'(?<=[.!?])\s+', text.strip()):
        chunks.extend(textwrap.wrap(sentence, width=112, break_long_words=False, break_on_hyphens=False))
    return chunks


def speech_excerpt(text, elapsed, duration):
    chunks = speech_chunks(text)
    if not chunks:
        return ''
    total = sum(len(chunk.split()) for chunk in chunks)
    target = max(0, min(elapsed / max(duration, .001), .999999)) * total
    cumulative = 0
    for chunk in chunks:
        cumulative += len(chunk.split())
        if target < cumulative:
            return chunk
    return chunks[-1]


def narration(text, elapsed, duration):
    excerpt = speech_excerpt(text, elapsed, duration)
    st.markdown(f'<div class="slide-copy">{escape(excerpt)}</div>', unsafe_allow_html=True)


def intro():
    st.markdown('''<div class="slide-eyebrow">COMPUTATIONAL THINKING · ASSIGNMENT 03</div>
    <div class="slide-brand">Lumen Travel</div>
    <div class="slide-subtitle">Trợ lý du lịch Thành phố Hồ Chí Minh</div>
    <div class="slide-author">Trần Hải Thiên &nbsp;·&nbsp; 25127007</div>''', unsafe_allow_html=True)


def cards(items):
    content = ''.join(f'<section class="slide-card"><h3>{escape(title)}</h3><p>{escape(text).replace(chr(10), "<br>")}</p></section>'
                      for title, text in items)
    st.markdown('<div class="slide-cards">'+content+'</div>', unsafe_allow_html=True)


def sources(result):
    entries = result['retrieved_entries']
    chips = ''.join(f'<span class="source-chip">[{escape(item["entry"]["id"])}] {escape(item["entry"]["title"])} · {item["score"]:.3f}</span>'
                    for item in entries)
    st.markdown('<div class="source-chips">'+chips+'</div>', unsafe_allow_html=True)
    cited = next((item['entry'] for item in entries if item['entry']['id'] in result['source_ids']), None)
    if cited:
        st.markdown(f'<div class="source-excerpt"><strong>[{escape(cited["id"])}] {escape(cited["title"])}</strong>'
                    f'<p>{escape(cited["text"])}</p><a href="{escape(cited["source"], quote=True)}" target="_blank" rel="noreferrer">Nguồn tham khảo ↗</a></div>', unsafe_allow_html=True)
    with st.expander('Chi tiết các mục được truy xuất'):
        for item in entries:
            entry = item['entry']
            st.markdown(f"**[{entry['id']}] {entry['title']}** · {item['score']:.3f}")
            st.write(entry['text'])
            st.link_button('Nguồn tham khảo', entry['source'])


def pipeline():
    nodes = [(20, 20, 'Đăng nhập', 'Email + mật khẩu', 'Phiên người dùng'),
             (390, 20, 'Embedding', 'Câu hỏi', 'Vector câu hỏi'),
             (760, 20, 'Truy xuất', 'Vector + chỉ mục', '3 mục và điểm số'),
             (760, 220, 'Ghép context', 'Câu hỏi + 3 mục', 'Prompt'),
             (390, 220, 'Sinh câu trả lời', 'Prompt', 'JSON đáp án'),
             (20, 220, 'Hiển thị', 'JSON + nguồn', 'Câu trả lời, lịch sử')]
    pieces = ['<svg width="100%" viewBox="0 0 1100 360" style="display:block;max-width:1100px;height:auto;margin:auto" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Sơ đồ sáu bước, đầu vào và đầu ra của từng bước">',
              '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="#73977e"/></marker></defs>',
              '<g fill="none" stroke="#73977e" stroke-width="2.5" marker-end="url(#arrow)"><path d="M340 80H385"/><path d="M710 80H755"/><path d="M920 140V212"/><path d="M760 280H718"/><path d="M390 280H348"/></g>']
    for index, (x, y, title, source, output) in enumerate(nodes, 1):
        pieces.append(f'<g transform="translate({x},{y})"><rect width="320" height="120" rx="16" fill="#eff4ec" stroke="#ccdaca"/>'
                      f'<text x="20" y="34" font-family="Arial,sans-serif" font-size="22" font-weight="bold" fill="#244331">{index}. {escape(title)}</text>'
                      f'<text x="20" y="69" font-family="Arial,sans-serif" font-size="18" fill="#526c58">Vào: {escape(source)}</text>'
                      f'<text x="20" y="98" font-family="Arial,sans-serif" font-size="18" fill="#526c58">Ra: {escape(output)}</text></g>')
    pieces.append('</svg>')
    st.image(''.join(pieces), width='stretch')
