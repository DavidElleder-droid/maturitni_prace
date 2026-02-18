SELECT
    o.id AS osoba_id,
    o.jmeno,
    o.prijmeni,
    o.cip
FROM dbo.osoby o
LEFT JOIN dbo.pruchod p
    ON p.cip = o.cip
    AND DATEADD(DAY, p.datum, '1900-01-01') = '2026-02-02'
WHERE p.cip IS NULL
ORDER BY o.prijmeni, o.jmeno;
