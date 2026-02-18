SELECT TOP 200
    DATEADD(DAY, p.datum, '1900-01-01')                     AS datum,
    CONVERT(time(0), DATEADD(SECOND, p.CAS, 0))             AS cas,
    p.cip                                                   AS cip,
    o.jmeno                                                 AS jmeno,
    o.prijmeni                                              AS prijmeni,
    o.id                                                    AS osoba_id
FROM dbo.pruchod p
JOIN dbo.osoby o ON p.cip = o.cip
WHERE DATEADD(DAY, p.datum, '1900-01-01') = '2026-02-02'
And CONVERT(time(0), DATEADD(SECOND, p.CAS, 0)) >= CONVERT(time, '00:08:15')
ORDER BY p.datum DESC, p.CAS DESC;
