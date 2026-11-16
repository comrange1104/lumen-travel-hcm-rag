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
