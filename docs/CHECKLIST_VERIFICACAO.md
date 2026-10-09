# Checklist: o que ainda falta confirmar

Restam **4 CAPS** com dado ausente na página oficial da unidade. Os demais já foram verificados e estão em `data/servicos.csv`.

## Pendências

- [ ] **CAPS III Gama** · Gama · `id: caps_iii_gama`
  - Falta: **telefone**. Também conferir o **horário** (a página diz dias úteis, 7h-22h; a Carta descreve o CAPS III como 24 horas).
  - Página: https://www.saude.df.gov.br/centro-de-atencao-psicossocial-gama-caps-iii
- [ ] **CAPS III Samambaia** · Samambaia · `id: caps_samambaia`
  - Falta: **telefone** e **horário geral de funcionamento** (a página só informa o horário do acolhimento).
  - Página: https://www.saude.df.gov.br/caps-iii-samambaia
- [ ] **CAPS AD III Samambaia** · Samambaia · `id: caps_ad_iii_samambaia`
  - Falta: **telefone** (a página informa 24 horas e o endereço).
  - Página: https://www.saude.df.gov.br/caps-ad-tipo-iii-samambaia
- [ ] **CAPS II Taguatinga** · Taguatinga · `id: caps_ii_taguatinga`
  - Falta: **endereço** (a página traz telefones e horário).
  - Página: https://www.saude.df.gov.br/caps-ii-taguatinga

## Onde procurar (somente fontes oficiais)

1. Na página oficial dos CAPS, o link **"Lista de endereços e contatos dos CAPS"** (https://www.saude.df.gov.br/carta-de-servicos-caps). Pode trazer os dados que as páginas das unidades não têm.
2. Contato direto com a SES-DF: a Ouvidoria (162) ou o formulário "Fale com a Secretaria" (https://www.saude.df.gov.br/fale-com-a-secretaria).
3. Se nada disso resolver, mantenha o status `confirmar`. O app já avisa o usuário.

## Como atualizar

1. Em `data/servicos.csv`, preencha o campo que faltava, ponha o link da fonte em `fonte` e a data em `data_consulta`.
2. Só troque `status` para `verificado` quando endereço **e** telefone estiverem confirmados.
3. Rode `python scripts/validar_dados.py` e `python scripts/pendencias.py`.
4. Faça commit e push.
