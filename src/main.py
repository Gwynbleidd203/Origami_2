from src.pdf import ResizePDF

resizer = ResizePDF(
    'J:/arquivos_digitalizados/licenciatura_em_educacao_fisica/em_andamento/licenciatura_em_educacao_fisica_2016(2)/',
    'J:/arquivos_digitalizados/licenciatura_em_educacao_fisica/finalizados/licenciatura_em_educacao_fisica_2016(2)/',
    "A4",
    order_by="name",
    use_custom_order=True
)