import { jsPDF } from "jspdf";

export const downloadReport = (result) => {

    const doc = new jsPDF();

    doc.setFontSize(22);
    doc.text("TruthLens Report", 20, 20);

    doc.setFontSize(14);

    doc.text(
        `Claim: ${result.claim || result.article_title}`,
        20,
        40
    );

    doc.text(
        `Verdict: ${result.verdict}`,
        20,
        55
    );

    doc.text(
        `Supports: ${result.supports}`,
        20,
        70
    );

    doc.text(
        `Contradicts: ${result.contradicts}`,
        20,
        85
    );

    doc.text(
        `Neutral: ${result.neutral}`,
        20,
        100
    );

    let y = 120;

    doc.text("Evidence Sources:", 20, y);

    result.analysis?.forEach((item, index) => {

        y += 15;

        doc.text(
            `${index + 1}. ${item.title}`,
            20,
            y
        );

    });

    y += 25;

    doc.text(
        `Generated: ${new Date().toLocaleString()}`,
        20,
        y
    );

    doc.save("TruthLens_Report.pdf");

};