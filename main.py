import polars as pl
import streamlit as st

questions_file = "questions.csv"

st.set_page_config(
    page_title="Leben in Deutschland Test",
    page_icon=":memo:",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# Functions
@st.cache_data
def load_data(file) -> pl.DataFrame:
    return pl.read_csv(file)


def restart() -> None:
    st.session_state.i = 0
    st.session_state.score = 0
    st.session_state.selected = None
    st.session_state.submitted = False
    return None


def submit(df) -> None:
    if st.session_state.selected is not None:
        st.session_state.submitted = True
        if st.session_state.selected == df[st.session_state.i]["answer"].item():
            st.session_state.score += 1
    else:
        st.warning("Select one answer")
    return None


def next():
    st.session_state.i += 1
    st.session_state.selected = None
    st.session_state.submitted = False


def main():
    # Setup
    quiz_df = load_data(questions_file)

    st.session_state.setdefault("i", 0)
    st.session_state.setdefault("score", 0)
    st.session_state.setdefault("selected", None)
    st.session_state.setdefault("submitted", False)

    # Page layout

    # Header
    st.title("Test «Leben in Deutschland»")

    # Question
    # Setup
    one_question_df = quiz_df[st.session_state.i]

    # Options
    options = [
        one_question_df.select(["option_1"]).item(),
        one_question_df.select(["option_2"]).item(),
        one_question_df.select(["option_3"]).item(),
        one_question_df.select(["option_4"]).item(),
    ]
    answer = one_question_df["answer"].item()

    # Display
    st.subheader(
        one_question_df["question"].item()
        + f" ({st.session_state.i + 1} / {len(quiz_df)})"
    )

    if st.session_state.submitted:
        for i, option in enumerate(options):
            label = option
            if option == answer:
                st.success(f"{label}", icon="✅")
            elif option == st.session_state.selected:
                st.error(f"{label}", icon="❌")
            else:
                st.info(label, icon="◻️")
    else:
        for i, option in enumerate(options):
            if st.button(option, key=i, use_container_width=True):
                st.session_state.selected = option

    if st.session_state.submitted:
        if st.session_state.i < len(quiz_df) - 1:
            st.button("Next", on_click=next, icon="➡️")
        else:
            st.write(
                f"Completed! Your score is: {st.session_state.score} / {len(quiz_df)}"
            )
            if st.button("Restart", on_click=restart):
                pass
    else:
        if st.session_state.i < len(quiz_df):
            st.button("Submit", on_click=submit(quiz_df))

    st.markdown(f"#### Correctly answered: {st.session_state.score}")

    st.markdown("##### Teil I. Allgemeine Fragen (Part I. General questions)")
    st.markdown(
        "##### Source: [BAMF - Leben in Deutschland](https://www.bamf.de/SharedDocs/Anlagen/DE/Integration/Einbuergerung/gesamtfragenkatalog-lebenindeutschland.pdf)"
    )


if __name__ == "__main__":
    main()
