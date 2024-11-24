import polars as pl
import streamlit as st

questions_file = "questions.csv"
questions_ru_file = "questions-ru.csv"

is_russian = False

st.set_page_config(
    page_title="Leben in Deutschland Test",
    page_icon=":memo:",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# Functions
# @st.cache_data
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
        answer = df[st.session_state.i]["answer"].item()

        if st.session_state.selected == answer:
            st.session_state.score += 1
    else:
        pass
    return None


def next():
    st.session_state.i += 1
    st.session_state.selected = None
    st.session_state.submitted = False


def main():
    # Setup
    quiz_df = load_data(questions_file)

    # Add translation to Russian
    is_russian = st.checkbox("Translate to Russian")

    if is_russian:
        quiz_ru_df = load_data(questions_ru_file)
        quiz_df = pl.concat([quiz_df, quiz_ru_df], how="horizontal")

        # Add to original strings the translation
        quiz_df = quiz_df.with_columns(
            question=pl.col("question") + " (" + pl.col("question_ru") + ")",
            option_1=pl.col("option_1") + " (" + pl.col("option_1_ru") + ")",
            option_2=pl.col("option_2") + " (" + pl.col("option_2_ru") + ")",
            option_3=pl.col("option_3") + " (" + pl.col("option_3_ru") + ")",
            option_4=pl.col("option_4") + " (" + pl.col("option_4_ru") + ")",
            answer=pl.col("answer") + " (" + pl.col("answer_ru") + ")",
        )

    st.session_state.setdefault("i", 0)
    st.session_state.setdefault("score", 0)
    st.session_state.setdefault("selected", None)
    st.session_state.setdefault("submitted", False)

    # Page layout
    # Header
    st.markdown("## Leben in Deutschland Test")

    # One question
    one_question_df = quiz_df[st.session_state.i]

    # Options
    options = [
        one_question_df["option_1"].item(),
        one_question_df["option_2"].item(),
        one_question_df["option_3"].item(),
        one_question_df["option_4"].item(),
    ]
    answer = one_question_df["answer"].item()

    # Display
    st.markdown(f"#### {one_question_df["question"].item()}")

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
            col1, col2, col3 = st.columns([6, 6.2, 2.35])
            col1.button("Submit", on_click=submit(quiz_df), type="primary")
            col2.button(f"Question {st.session_state.i + 1} / {len(quiz_df)}")
            col3.button(f"Correctly: {st.session_state.score}  ")

    # Get from user the question number to jump to (slider)
    col1, col2 = st.columns([1, 3])

    question_number = st.slider(
        label="Select another question",
        min_value=1,
        max_value=len(quiz_df),
        value=1,
    )

    def jump_to_question():
        st.session_state.i = question_number - 1

    if st.button("Jump to question", on_click=jump_to_question):
        pass

    # Footer
    st.markdown("---")
    st.markdown(
        "###### Source: [BAMF - Leben in Deutschland](https://www.bamf.de/SharedDocs/Anlagen/DE/Integration/Einbuergerung/gesamtfragenkatalog-lebenindeutschland.pdf) (Teil I. Allgemeine Fragen (Part I. General questions))"
    )


if __name__ == "__main__":
    main()
