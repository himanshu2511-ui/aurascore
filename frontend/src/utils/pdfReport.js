import jsPDF from 'jspdf';

/**
 * Generates a comprehensive AuraScore PDF report from analysis snapshots.
 * @param {Array} snapshots - Array of analysis results collected over 40 seconds
 * @param {Object} finalAnalysis - The last/best analysis snapshot
 * @param {string} sessionDate - Date string for the report
 */
export function generateAuraPDF(snapshots, finalAnalysis, sessionDate) {
    const doc = new jsPDF({ unit: 'mm', format: 'a4' });
    const W = 210; // A4 width
    const margin = 18;
    let y = 20;

    // ── Helpers ──────────────────────────────────────────────────────────────
    const line = (x1, y1, x2, y2, color = [40, 40, 60]) => {
        doc.setDrawColor(...color);
        doc.line(x1, y1, x2, y2);
    };
    const rect = (x, yy, w, h, fill, stroke) => {
        if (fill) doc.setFillColor(...fill);
        if (stroke) doc.setDrawColor(...stroke);
        doc.rect(x, yy, w, h, fill && stroke ? 'FD' : fill ? 'F' : 'S');
    };
    const text = (str, x, yy, opts = {}) => {
        if (opts.color) doc.setTextColor(...opts.color);
        if (opts.size) doc.setFontSize(opts.size);
        if (opts.bold) doc.setFont('helvetica', 'bold');
        else doc.setFont('helvetica', 'normal');
        doc.text(str, x, yy, { align: opts.align || 'left' });
    };
    const newPage = () => {
        doc.addPage();
        y = 20;
        // subtle header band
        rect(0, 0, W, 10, [12, 12, 22]);
        text('AuraScore AI Report', W / 2, 7, { color: [240, 192, 64], size: 8, align: 'center' });
    };
    const checkPage = (needed = 20) => {
        if (y + needed > 278) newPage();
    };

    // Compute averages from snapshots
    const avg = (key) => {
        const vals = snapshots.map(s => s[key]).filter(v => v != null && !isNaN(v));
        return vals.length ? Math.round(vals.reduce((a, b) => a + b, 0) / vals.length) : 0;
    };
    const avgFeature = (featureName, field) => {
        const vals = snapshots
            .flatMap(s => s.features || [])
            .filter(f => f.name === featureName)
            .map(f => f[field]);
        return vals.length ? Math.round(vals.reduce((a, b) => a + b, 0) / vals.length) : 0;
    };

    const avgBaseline = avg('baseline_score');
    const avgPotential = avg('potential_score');
    const stability = Math.round((1 - (Math.max(...snapshots.map(s => s.baseline_score)) - Math.min(...snapshots.map(s => s.baseline_score))) / 100) * 100);

    // ── COVER PAGE ────────────────────────────────────────────────────────────
    rect(0, 0, W, 297, [8, 8, 18]); // dark bg

    // Gold accent bar top
    rect(0, 0, W, 6, [240, 192, 64]);

    // Title block
    doc.setFontSize(28);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(240, 192, 64);
    doc.text('AuraScore', W / 2, 55, { align: 'center' });

    doc.setFontSize(13);
    doc.setTextColor(200, 200, 220);
    doc.text('AI Glow-Up Intelligence Report', W / 2, 65, { align: 'center' });

    doc.setFontSize(9);
    doc.setTextColor(100, 100, 130);
    doc.text(`Session: ${sessionDate}  |  Snapshots: ${snapshots.length}  |  Duration: ~40 seconds`, W / 2, 73, { align: 'center' });

    // Big dual score
    const scoreBoxW = 70;
    const bx = W / 2 - scoreBoxW - 5;
    const px = W / 2 + 5;

    rect(bx, 85, scoreBoxW, 50, [20, 20, 40], [155, 93, 229]);
    rect(px, 85, scoreBoxW, 50, [20, 20, 40], [240, 192, 64]);

    text('YOUR BASELINE', bx + scoreBoxW / 2, 93, { color: [155, 93, 229], size: 7, align: 'center' });
    text(`${avgBaseline}`, bx + scoreBoxW / 2, 114, { color: [220, 220, 255], size: 30, bold: true, align: 'center' });
    text('/100', bx + scoreBoxW / 2, 122, { color: [100, 100, 140], size: 8, align: 'center' });

    text('YOUR POTENTIAL', px + scoreBoxW / 2, 93, { color: [240, 192, 64], size: 7, align: 'center' });
    text(`${avgPotential}`, px + scoreBoxW / 2, 114, { color: [240, 230, 180], size: 30, bold: true, align: 'center' });
    text('/100', px + scoreBoxW / 2, 122, { color: [140, 130, 80], size: 8, align: 'center' });

    text('- with recommended improvements', W / 2, 143, { color: [100, 100, 130], size: 8, align: 'center' });

    // Face shape + stability
    rect(margin, 155, W - margin * 2, 28, [16, 16, 30], [40, 40, 70]);
    text('FACE SHAPE', margin + 10, 163, { color: [155, 93, 229], size: 7 });
    text(finalAnalysis?.face_shape || 'Oval', margin + 10, 172, { color: [200, 200, 240], size: 14, bold: true });
    text('SCAN STABILITY', W / 2 + 10, 163, { color: [155, 93, 229], size: 7 });
    text(`${stability}%`, W / 2 + 10, 172, { color: [38, 255, 138], size: 14, bold: true });
    text('detection consistency', W / 2 + 10, 178, { color: [80, 100, 80], size: 7 });

    // Disclaimer
    doc.setFontSize(7);
    doc.setTextColor(70, 70, 90);
    const disclaimer = 'AI estimates based on geometric analysis - not absolute truths. Scores reflect improvement potential, not personal worth.';
    doc.text(disclaimer, W / 2, 287, { align: 'center', maxWidth: 170 });
    rect(0, 291, W, 6, [240, 192, 64]);

    // ── PAGE 2: Feature Breakdown ─────────────────────────────────────────────
    newPage();
    y = 18;

    text('Feature Analysis', margin, y, { color: [240, 192, 64], size: 16, bold: true });
    y += 5;
    text('Averaged across all 40-second session snapshots', margin, y, { color: [100, 100, 130], size: 8 });
    y += 9;
    line(margin, y, W - margin, y, [40, 40, 70]);
    y += 8;

    const features = finalAnalysis?.features || [];
    const catColors = {
        genetics: [155, 93, 229],
        grooming: [0, 229, 255],
        fitness: [38, 255, 138],
        skin: [240, 192, 64],
        style: [255, 140, 66],
    };

    features.forEach((feat) => {
        checkPage(38);
        const avgBase = avgFeature(feat.name, 'baseline');
        const avgPot = avgFeature(feat.name, 'potential');
        const catCol = catColors[feat.category] || [180, 180, 180];

        doc.setFontSize(6.5);
        const tipLines = doc.splitTextToSize(`Tip: ${feat.tip}`, W - margin * 2 - 6);
        const boxH = 26 + tipLines.length * 2.5;

        rect(margin, y, W - margin * 2, boxH, [14, 14, 26], [30, 30, 50]);

        // Category badge
        doc.setFillColor(catCol[0] * 0.25, catCol[1] * 0.25, catCol[2] * 0.25);
        doc.roundedRect(margin + 3, y + 3, 22, 6, 2, 2, 'F');
        text(feat.category.toUpperCase(), margin + 14, y + 7.5, { color: catCol, size: 5.5, align: 'center' });

        text(feat.name, margin + 28, y + 8, { color: [220, 220, 240], size: 10, bold: true });

        // Baseline bar
        const barX = margin + 3;
        const barW = W - margin * 2 - 6;
        const barY = y + 14;

        // Potential (ghost) bar
        rect(barX, barY, barW * (avgPot / 100), 5, [...catColors.genetics.map(c => Math.round(c * 0.3))]);

        // Baseline (solid) bar
        doc.setFillColor(...catCol);
        doc.rect(barX, barY, barW * (avgBase / 100), 5, 'F');

        // Track background
        doc.setDrawColor(40, 40, 60);
        doc.rect(barX, barY, barW, 5, 'S');

        text(`${avgBase}/100`, barX + barW * (avgBase / 100) + 2, barY + 4.5, { color: catCol, size: 7, bold: true });
        text(`Potential: ${avgPot}`, W - margin - 3, barY + 4.5, { color: [140, 140, 160], size: 6.5, align: 'right' });

        // Tip
        doc.setTextColor(100, 100, 120);
        doc.text(tipLines, margin + 3, y + 24.5);

        y += boxH + 5;
    });

    // ── PAGE 3: Skin Intelligence ────────────────────────────────────────────
    newPage();
    y = 18;

    text('Skin Intelligence Report', margin, y, { color: [240, 192, 64], size: 16, bold: true });
    y += 5;
    line(margin, y, W - margin, y, [40, 40, 70]);
    y += 10;

    const skin = finalAnalysis?.skin;
    if (skin) {
        const stats = [
            { label: 'Skin Tone', value: skin.skin_tone, col: [240, 192, 64] },
            { label: 'Texture Score', value: `${skin.texture_score}/100`, col: skin.texture_score >= 75 ? [38, 255, 138] : [255, 140, 66] },
            { label: 'Dark Circles', value: skin.dark_circle_severity, col: skin.dark_circle_severity === 'None' ? [38, 255, 138] : [255, 100, 100] },
            { label: 'Skin Tier', value: skin.skin_tier, col: skin.skin_tier === 'Clean' ? [38, 255, 138] : [255, 80, 80] },
        ];

        const statW = (W - margin * 2 - 9) / 4;
        stats.forEach((s, i) => {
            const sx = margin + i * (statW + 3);
            rect(sx, y, statW, 28, [16, 16, 28], [35, 35, 55]);
            text(s.label.toUpperCase(), sx + 3, y + 8, { color: [100, 100, 130], size: 6 });
            text(s.value, sx + 3, y + 18, { color: s.col, size: 10, bold: true });
        });
        y += 36;

        text('Personalised Skincare Recommendations', margin, y, { color: [200, 200, 220], size: 11, bold: true });
        y += 8;
        (skin.skincare_tips || []).forEach((tip, i) => {
            doc.setFontSize(8);
            const lines = doc.splitTextToSize(tip, W - margin * 2 - 14);
            const boxH = 5 + lines.length * 3.5;
            checkPage(boxH + 4);
            rect(margin, y, W - margin * 2, boxH, [14, 14, 24], [30, 30, 50]);
            text(`${i + 1}.`, margin + 3, y + 7, { color: [240, 192, 64], size: 8, bold: true });
            doc.setFontSize(8);
            doc.setTextColor(170, 170, 190);
            doc.setFont('helvetica', 'normal');
            doc.text(lines, margin + 10, y + 7);
            y += boxH + 3;
        });
    }

    // ── PAGE 4: Grooming & Style ──────────────────────────────────────────────
    newPage();
    y = 18;

    text('Grooming & Style Guide', margin, y, { color: [240, 192, 64], size: 16, bold: true });
    y += 5;
    line(margin, y, W - margin, y, [40, 40, 70]);
    y += 10;

    const grooming = finalAnalysis?.grooming;
    if (grooming) {
        text(`Face Shape: ${grooming.face_shape}`, margin, y, { color: [155, 93, 229], size: 13, bold: true });
        y += 10;

        const sections = [
            { icon: '[Hair]', label: 'Recommended Hairstyles', items: grooming.hairstyles },
            { icon: '[Beard]', label: 'Beard Style Suggestions', items: grooming.beard_styles },
            { icon: '[Frames]', label: 'Best Glasses Frames', items: grooming.glasses_frames },
            { icon: '[Tips]', label: 'Pro Styling Tips', items: grooming.style_tips },
        ];

        sections.forEach((sec) => {
            checkPage(30);
            text(`${sec.icon} ${sec.label}`, margin, y, { color: [200, 200, 240], size: 10, bold: true });
            y += 6;
            sec.items.forEach((item) => {
                doc.setFontSize(8);
                const lines = doc.splitTextToSize(`-  ${item}`, W - margin * 2 - 8);
                const boxH = 4 + lines.length * 3.5;
                checkPage(boxH + 2);
                rect(margin, y, W - margin * 2, boxH, [14, 14, 26], [30, 30, 50]);
                doc.setTextColor(160, 160, 180);
                doc.setFont('helvetica', 'normal');
                doc.text(lines, margin + 4, y + 5.5);
                y += boxH + 2;
            });
            y += 4;
        });
    }

    // ── PAGE 5: 8-Week Roadmap ────────────────────────────────────────────────
    newPage();
    y = 18;

    text('Your 8-Week Glow-Up Roadmap', margin, y, { color: [240, 192, 64], size: 16, bold: true });
    y += 5;
    line(margin, y, W - margin, y, [40, 40, 70]);
    y += 10;

    (finalAnalysis?.roadmap || []).forEach((week, wi) => {
        checkPage(50);
        rect(margin, y, W - margin * 2, 8, [155, 93, 229].map(c => Math.round(c * 0.2)), [35, 35, 65]);
        text(`${week.week}  -  ${week.focus}`, margin + 4, y + 5.5, { color: [200, 200, 240], size: 9, bold: true });
        y += 11;

        (week.goals || []).forEach((goal) => {
            doc.setFontSize(7.5);
            const lines = doc.splitTextToSize(`-  ${goal}`, W - margin * 2 - 8);
            const boxH = 4 + lines.length * 3;
            checkPage(boxH + 2);
            rect(margin, y, W - margin * 2, boxH, [12, 12, 22], [25, 25, 45]);
            doc.setTextColor(140, 140, 160);
            doc.setFont('helvetica', 'normal');
            doc.text(lines, margin + 4, y + 5.5);
            y += boxH + 2;
        });
        y += 5;
    });

    // ── BACK COVER ────────────────────────────────────────────────────────────
    doc.addPage();
    rect(0, 0, W, 297, [8, 8, 18]);
    rect(0, 0, W, 6, [240, 192, 64]);
    rect(0, 291, W, 6, [240, 192, 64]);

    text('AuraScore', W / 2, 130, { color: [240, 192, 64], size: 22, bold: true, align: 'center' });
    text('Transform. Improve. Glow Up.', W / 2, 142, { color: [155, 93, 229], size: 10, align: 'center' });

    const mantras = [
        '"Your genetics are a foundation, not a ceiling."',
        '"Every improvement starts with awareness."',
        '"Consistency beats perfection every time."',
    ];
    mantras.forEach((m, i) => {
        text(m, W / 2, 165 + i * 12, { color: [80, 80, 100], size: 8, align: 'center' });
    });

    text(`Report generated by AuraScore AI  |  ${sessionDate}`, W / 2, 290, { color: [60, 60, 80], size: 7, align: 'center' });

    // Save
    doc.save(`AuraScore_Report_${Date.now()}.pdf`);
}
