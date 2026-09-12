import pytest

from app.service.csv_import import (
    CsvFormatError,
    parse_criteria_csv,
    parse_questions_csv,
)


def test_parse_questions_csv_builds_one_question_per_row() -> None:
    content = (
        "id,prompt,max_score,score_increment\n"
        "1.1,What is a prototype?,10,1\n"
        "1.2,Why prototype?,5,0.5\n"
    )

    questions = parse_questions_csv(content)

    assert [question.external_id for question in questions] == ["1.1", "1.2"]
    assert questions[0].prompt == "What is a prototype?"
    assert questions[0].max_score == 10
    assert questions[1].score_increment == 0.5


def test_parse_questions_csv_rejects_missing_column() -> None:
    content = "id,prompt,max_score\n1.1,What is a prototype?,10\n"

    with pytest.raises(CsvFormatError, match="score_increment"):
        parse_questions_csv(content)


def test_parse_questions_csv_rejects_duplicate_id() -> None:
    content = (
        "id,prompt,max_score,score_increment\n"
        "1.1,First,10,1\n"
        "1.1,Second,5,1\n"
    )

    with pytest.raises(CsvFormatError, match="duplicate question id '1.1'"):
        parse_questions_csv(content)


def test_parse_questions_csv_rejects_non_numeric_score() -> None:
    content = "id,prompt,max_score,score_increment\n1.1,What is a prototype?,ten,1\n"

    with pytest.raises(CsvFormatError, match="max_score"):
        parse_questions_csv(content)


def test_parse_questions_csv_rejects_empty_file() -> None:
    content = "id,prompt,max_score,score_increment\n"

    with pytest.raises(CsvFormatError, match="no data rows"):
        parse_questions_csv(content)


def test_parse_criteria_csv_groups_rows_by_id() -> None:
    content = (
        "id,criteria,criteria_max_score,model_answer\n"
        "1.1,Mentions simulating behaviour,1,To simulate the behaviour of the product.\n"
        "1.1,Mentions risk reduction,1,To simulate the behaviour of the product.\n"
        "1.2,Mentions cost savings,2,\n"
    )

    rubrics = parse_criteria_csv(content)

    assert set(rubrics) == {"1.1", "1.2"}
    assert len(rubrics["1.1"].criteria) == 2
    assert rubrics["1.1"].model_answer == "To simulate the behaviour of the product."
    assert rubrics["1.2"].model_answer is None


def test_parse_criteria_csv_rejects_conflicting_model_answer_for_same_question() -> None:
    content = (
        "id,criteria,criteria_max_score,model_answer\n"
        "1.1,First criterion,1,Answer A\n"
        "1.1,Second criterion,1,Answer B\n"
    )

    with pytest.raises(CsvFormatError, match="conflicts with an earlier row"):
        parse_criteria_csv(content)


def test_parse_criteria_csv_rejects_missing_column() -> None:
    content = "id,criteria,model_answer\n1.1,Mentions X,Some answer\n"

    with pytest.raises(CsvFormatError, match="criteria_max_score"):
        parse_criteria_csv(content)
