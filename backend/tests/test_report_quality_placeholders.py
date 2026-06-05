from services.report_quality import _strip_report_placeholders


def test_strip_report_placeholders_removes_do_not_undo_markers():
    text = "Heading\nDO_NOT_UNDO\n\nBody line\nDO NOT UNDO\nFooter"

    cleaned = _strip_report_placeholders(text)

    assert "DO_NOT_UNDO" not in cleaned
    assert "DO NOT UNDO" not in cleaned
    assert "Body line" in cleaned
