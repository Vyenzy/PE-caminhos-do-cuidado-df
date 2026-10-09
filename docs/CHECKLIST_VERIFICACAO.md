# Checklist: verificação dos endereços pendentes

São **16 CAPS** com existência e tipo confirmados na lista oficial da SES-DF, mas sem endereço e telefone no repositório. Cada item abaixo leva à página oficial da unidade.

## Como verificar

1. Abra o link da unidade e localize **endereço**, **telefone** e, se houver, **horário de funcionamento**.
2. Copie **exatamente** como está na página (não reescreva, não complete de memória).
3. Se a página **não** trouxer alguma informação, deixe "A CONFIRMAR" nesse campo e mantenha o status `confirmar`. Não use outros sites para preencher.
4. Em `data/servicos.csv`, na linha da unidade (`id` indicado abaixo), atualize:
   - `endereco`, `telefone` (e `horario`, se a página informar);
   - `fonte` → o link da página da unidade;
   - `data_consulta` → a data de hoje (AAAA-MM-DD);
   - `status` → `verificado` (só se endereço **e** telefone estiverem confirmados);
   - `observacao` → remova o trecho "Endereço e telefone: ..." e deixe o que ainda for relevante.
5. Rode `python scripts/validar_dados.py` e depois `python scripts/pendencias.py` para ver o que falta.
6. Faça um commit pequeno a cada lote (ex.: `Verifica CAPS de Taguatinga`).

## Unidades

- [ ] **CAPS III Gama** · Gama · `id: caps_iii_gama`
  - Página oficial: https://www.saude.df.gov.br/centro-de-atencao-psicossocial-gama-caps-iii
  - Endereço: 
  - Telefone: 
  - Horário (se a página informar): 
- [ ] **CAPS AD Guará** · Guará · `id: caps_ad_guara`
  - Página oficial: https://www.saude.df.gov.br/caps-ad-guara
  - Endereço: 
  - Telefone: 
  - Horário (se a página informar): 
- [ ] **CAPS AD II Itapoã** · Itapoã · `id: caps_ad_ii_itapoa`
  - Página oficial: https://www.saude.df.gov.br/caps-ad-ii-itapoa
  - Endereço: 
  - Telefone: 
  - Horário (se a página informar): 
- [ ] **CAPS II Paranoá** · Paranoá · `id: caps_ii_paranoa`
  - Página oficial: https://www.saude.df.gov.br/caps-ii-paranoa
  - Endereço: 
  - Telefone: 
  - Horário (se a página informar): 
- [ ] **CAPS II Planaltina** · Planaltina · `id: caps_ii_planaltina`
  - Página oficial: https://www.saude.df.gov.br/caps-ii-planaltina
  - Endereço: 
  - Telefone: 
  - Horário (se a página informar): 
- [ ] **CAPS II Brasília (Asa Norte)** · Plano Piloto (Asa Norte) · `id: caps_ii_brasilia`
  - Página oficial: https://www.saude.df.gov.br/asanorte-brasilia-caps-ii
  - Endereço: 
  - Telefone: 
  - Horário (se a página informar): 
- [ ] **CAPS i Asa Norte** · Plano Piloto (Asa Norte) · `id: capsi_asa_norte`
  - Página oficial: https://www.saude.df.gov.br/caps-1-asa-norte
  - Endereço: 
  - Telefone: 
  - Horário (se a página informar): 
- [ ] **CAPS i Recanto das Emas** · Recanto das Emas · `id: capsi_recanto`
  - Página oficial: https://www.saude.df.gov.br/capsi-recanto-das-emas
  - Endereço: 
  - Telefone: 
  - Horário (se a página informar): 
- [ ] **CAPS II Riacho Fundo** · Riacho Fundo · `id: caps_riacho_fundo`
  - Página oficial: https://www.saude.df.gov.br/caps-ii-riacho-fundo
  - Endereço: 
  - Telefone: 
  - Horário (se a página informar): 
- [ ] **CAPS AD III Samambaia** · Samambaia · `id: caps_ad_iii_samambaia`
  - Página oficial: https://www.saude.df.gov.br/caps-ad-tipo-iii-samambaia
  - Endereço: 
  - Telefone: 
  - Horário (se a página informar): 
- [ ] **CAPS III Samambaia** · Samambaia · `id: caps_samambaia`
  - Página oficial: https://www.saude.df.gov.br/caps-iii-samambaia
  - Endereço: 
  - Telefone: 
  - Horário (se a página informar): 
- [ ] **CAPS II Santa Maria** · Santa Maria · `id: caps_ii_santa_maria`
  - Página oficial: https://www.saude.df.gov.br/caps-ii-santa-maria
  - Endereço: 
  - Telefone: 
  - Horário (se a página informar): 
- [ ] **CAPS AD Sobradinho** · Sobradinho · `id: caps_ad_sobradinho`
  - Página oficial: https://www.saude.df.gov.br/caps-ad-sobradinho
  - Endereço: 
  - Telefone: 
  - Horário (se a página informar): 
- [ ] **CAPS i Sobradinho** · Sobradinho · `id: capsi_sobradinho`
  - Página oficial: https://www.saude.df.gov.br/capsi-sobradinho
  - Endereço: 
  - Telefone: 
  - Horário (se a página informar): 
- [ ] **CAPS II Taguatinga** · Taguatinga · `id: caps_ii_taguatinga`
  - Página oficial: https://www.saude.df.gov.br/caps-ii-taguatinga
  - Endereço: 
  - Telefone: 
  - Horário (se a página informar): 
- [ ] **CAPS i Taguatinga** · Taguatinga · `id: capsi_taguatinga`
  - Página oficial: https://www.saude.df.gov.br/capsi-taguatinga
  - Endereço: 
  - Telefone: 
  - Horário (se a página informar): 

## Dica para o relatório

Registre no PROJETO.md quantas unidades foram verificadas e quantas ficaram pendentes (e por quê). Isso mostra rigor e transparência.
