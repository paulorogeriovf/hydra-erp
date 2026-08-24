// Hydra ERP
// Responsável por: controlar a montagem, cálculo, cópia
// e geração de PDF dos orçamentos.


let produtos = [];

const carrinho = {};


const appOrcamento = document.getElementById("orcamentoApp");

const apiProdutosUrl = appOrcamento.dataset.apiUrl;
const logoUrl = appOrcamento.dataset.logoUrl;


const divProdutos = document.getElementById("produtos");
const totalSpan = document.getElementById("total");
const campoBusca = document.getElementById("campoBusca");
const descontoInput = document.getElementById("desconto");


/* =========================================================
   CARREGAR PRODUTOS
========================================================= */

async function carregarProdutos() {

    try {

        const resposta = await fetch(apiProdutosUrl);

        if (!resposta.ok) {
            throw new Error("Não foi possível carregar os produtos.");
        }

        produtos = await resposta.json();

        renderizarProdutos();

        atualizarTotal();

    } catch (erro) {

        console.error(
            "Erro ao carregar produtos:",
            erro
        );

        divProdutos.innerHTML = `
            <div class="orcamento-carregando">
                ❌ Não foi possível carregar os produtos.
            </div>
        `;

    }

}


/* =========================================================
   RENDERIZAR PRODUTOS
========================================================= */

function renderizarProdutos(filtro = "") {

    divProdutos.innerHTML = "";

    const grupos = {};


    produtos
        .filter(produto => {

            const busca = filtro
                .trim()
                .toLowerCase();

            const nome = produto.nome
                .toLowerCase();

            const marca = (
                produto.marca || ""
            ).toLowerCase();

            return (
                nome.includes(busca) ||
                marca.includes(busca)
            );

        })
        .forEach(produto => {

            const categoria =
                produto.categoria || "Outros";

            if (!grupos[categoria]) {
                grupos[categoria] = [];
            }

            grupos[categoria].push(produto);

        });


    const categorias = Object.keys(grupos);


    if (categorias.length === 0) {

        divProdutos.innerHTML = `
            <div class="orcamento-carregando">
                Nenhum produto encontrado.
            </div>
        `;

        return;

    }


    categorias.forEach(categoria => {

        const titulo = document.createElement("div");

        titulo.className =
            "orcamento-categoria";

        titulo.textContent =
            categoria;

        divProdutos.appendChild(titulo);


        grupos[categoria].forEach(produto => {

            const quantidade =
                carrinho[produto.id] || 0;


            const div =
                document.createElement("div");


            div.className =
                "orcamento-produto";


            div.innerHTML = `

                <div>

                    <span class="orcamento-produto-nome">
                        ${produto.nome}
                    </span>

                    ${
                        produto.marca
                            ? `
                                <span class="orcamento-produto-marca">
                                    ${produto.marca}
                                </span>
                              `
                            : ""
                    }

                </div>


                <div class="orcamento-controle">

                    <button
                        type="button"
                        onclick="alterarQtd(${produto.id}, -1)"
                    >
                        −
                    </button>


                    <input
                        type="number"
                        min="0"
                        value="${quantidade}"
                        onchange="setarQtd(${produto.id}, this.value)"
                    >


                    <button
                        type="button"
                        onclick="alterarQtd(${produto.id}, 1)"
                    >
                        +
                    </button>

                </div>


                <span class="orcamento-preco">
                    ${formatarMoeda(produto.preco)}
                </span>

            `;


            divProdutos.appendChild(div);

        });

    });

}


/* =========================================================
   QUANTIDADE
========================================================= */

function alterarQtd(produtoId, valor) {

    if (!carrinho[produtoId]) {
        carrinho[produtoId] = 0;
    }


    carrinho[produtoId] += valor;


    if (carrinho[produtoId] < 0) {
        carrinho[produtoId] = 0;
    }


    atualizarTotal();

    renderizarProdutos(
        campoBusca.value
    );

}


function setarQtd(produtoId, valor) {

    let quantidade =
        Number(valor) || 0;


    if (quantidade < 0) {
        quantidade = 0;
    }


    carrinho[produtoId] = quantidade;

    atualizarTotal();

}


/* =========================================================
   CÁLCULOS
========================================================= */

function calcularOrcamento() {

    let subtotal = 0;


    produtos.forEach(produto => {

        const quantidade =
            carrinho[produto.id] || 0;


        subtotal +=
            quantidade * produto.preco;

    });


    let desconto =
        Number(descontoInput.value) || 0;


    if (desconto < 0) {
        desconto = 0;
    }


    if (desconto > 100) {
        desconto = 100;
    }


    const valorDesconto =
        subtotal * (desconto / 100);


    const total =
        subtotal - valorDesconto;


    return {
        subtotal,
        desconto,
        valorDesconto,
        total
    };

}


function atualizarTotal() {

    const calculo =
        calcularOrcamento();


    totalSpan.textContent =
        calculo.total.toLocaleString(
            "pt-BR",
            {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }
        );

}


/* =========================================================
   BUSCA
========================================================= */

campoBusca.addEventListener(
    "input",
    evento => {

        renderizarProdutos(
            evento.target.value
        );

    }
);


descontoInput.addEventListener(
    "input",
    atualizarTotal
);


/* =========================================================
   GERAR TEXTO
========================================================= */

document
    .getElementById("btnGerar")
    .addEventListener(
        "click",
        gerarTextoOrcamento
    );


function gerarTextoOrcamento() {

    const nome =
        document
            .getElementById("nomeCliente")
            .value
            .trim();


    const calculo =
        calcularOrcamento();


    let texto =
        "🧾 Orçamento Hydra Piscinas\n";


    if (nome) {
        texto += `Cliente: ${nome}\n`;
    }


    texto += "\n";


    let possuiProduto = false;


    produtos.forEach(produto => {

        const quantidade =
            carrinho[produto.id] || 0;


        if (quantidade > 0) {

            possuiProduto = true;


            const subtotal =
                quantidade *
                produto.preco;


            texto +=
                `${produto.nome} - ` +
                `${quantidade} un - ` +
                `${formatarMoeda(subtotal)}\n`;

        }

    });


    if (!possuiProduto) {

        alert(
            "Selecione pelo menos um produto."
        );

        return;

    }


    if (calculo.desconto > 0) {

        texto +=
            `\nDesconto (${calculo.desconto}%): ` +
            `-${formatarMoeda(calculo.valorDesconto)}\n`;

    }


    texto +=
        `\nTOTAL: ${formatarMoeda(calculo.total)}`;


    document
        .getElementById("resultado")
        .textContent = texto;


    document
        .getElementById("resultadoContainer")
        .style.display = "block";

}


/* =========================================================
   COPIAR
========================================================= */

document
    .getElementById("btnCopiar")
    .addEventListener(
        "click",
        copiarOrcamento
    );


async function copiarOrcamento() {

    const resultado =
        document.getElementById("resultado");


    if (!resultado.textContent.trim()) {

        gerarTextoOrcamento();

    }


    const texto =
        resultado.textContent;


    if (!texto.trim()) {
        return;
    }


    try {

        await navigator.clipboard.writeText(
            texto
        );


        mostrarCopiado();

    } catch (erro) {

        const textarea =
            document.createElement("textarea");


        textarea.value = texto;


        document.body.appendChild(
            textarea
        );


        textarea.select();


        document.execCommand("copy");


        textarea.remove();


        mostrarCopiado();

    }

}


function mostrarCopiado() {

    const botao =
        document.getElementById("btnCopiar");


    const textoOriginal =
        botao.innerHTML;


    botao.innerHTML =
        "✅ Copiado!";


    setTimeout(() => {

        botao.innerHTML =
            textoOriginal;

    }, 2000);

}


/* =========================================================
   PDF
========================================================= */

document
    .getElementById("btnPDF")
    .addEventListener(
        "click",
        gerarPDF
    );


async function gerarPDF() {

    const itens =
        produtos.filter(produto => {

            return (
                carrinho[produto.id] || 0
            ) > 0;

        });


    if (itens.length === 0) {

        alert(
            "Selecione pelo menos um produto."
        );

        return;

    }


    const {
        jsPDF
    } = window.jspdf;


    const doc =
        new jsPDF(
            "p",
            "mm",
            "a4"
        );


    const nome =
        document
            .getElementById("nomeCliente")
            .value
            .trim() ||
        "Não informado";


    const calculo =
        calcularOrcamento();


    let y = 20;


    /* =====================================================
       CABEÇALHO
    ===================================================== */

    doc.setFillColor(
        0,
        102,
        204
    );


    doc.rect(
        15,
        y - 5,
        180,
        25,
        "F"
    );


    doc.setFontSize(16);


    doc.setTextColor(
        255,
        255,
        255
    );


    doc.setFont(
        "helvetica",
        "bold"
    );


    doc.text(
        "Hydra Piscinas - Orçamento",
        20,
        y + 5
    );


    /* =====================================================
       LOGO
    ===================================================== */

    try {

        const logoBase64 =
            await carregarLogoBase64(
                logoUrl
            );


        doc.addImage(
            logoBase64,
            "JPEG",
            150,
            y - 5,
            50,
            40
        );

    } catch (erro) {

        console.error(
            "Não foi possível carregar a logo:",
            erro
        );

    }


    y += 28;


    /* =====================================================
       CLIENTE / EMPRESA
    ===================================================== */

    doc.setFontSize(12);


    doc.setTextColor(
        0,
        0,
        0
    );


    doc.setFont(
        "helvetica",
        "normal"
    );


    doc.text(
        `CNPJ Hydra Piscinas 37.526.566/0001-61\nCliente: ${nome}`,
        20,
        y
    );


    y += 14;


    /* =====================================================
       CABEÇALHO DA TABELA
    ===================================================== */

    doc.setFont(
        "helvetica",
        "bold"
    );


    doc.text(
        "Produto",
        20,
        y
    );


    doc.text(
        "Qtd",
        140,
        y,
        {
            align: "right"
        }
    );


    doc.text(
        "Subtotal",
        180,
        y,
        {
            align: "right"
        }
    );


    y += 4;


    doc.line(
        20,
        y,
        180,
        y
    );


    y += 7;


    doc.setFont(
        "helvetica",
        "normal"
    );


    /* =====================================================
       PRODUTOS
    ===================================================== */

    itens.forEach(
        (produto, indice) => {

            const quantidade =
                carrinho[produto.id];


            const subtotal =
                quantidade *
                produto.preco;


            /* Nova página caso necessário */
            if (y > 270) {

                doc.addPage();

                y = 20;

            }


            /* Linha alternada */
            if (indice % 2 === 0) {

                doc.setFillColor(
                    245,
                    248,
                    250
                );


                doc.rect(
                    20,
                    y - 4,
                    160,
                    7,
                    "F"
                );

            }


            const nomeProduto =
                produto.nome.length > 50
                    ? produto.nome.substring(
                        0,
                        47
                      ) + "..."
                    : produto.nome;


            doc.text(
                nomeProduto,
                20,
                y
            );


            doc.text(
                String(quantidade),
                140,
                y,
                {
                    align: "right"
                }
            );


            doc.text(
                formatarMoedaPDF(
                    subtotal
                ),
                180,
                y,
                {
                    align: "right"
                }
            );


            y += 7;

        }
    );


    /* =====================================================
       DESCONTO
    ===================================================== */

    if (calculo.desconto > 0) {

        y += 5;


        doc.setFont(
            "helvetica",
            "bold"
        );


        doc.setTextColor(
            200,
            0,
            0
        );


        doc.text(
            `Desconto (${calculo.desconto}%): -${formatarMoedaPDF(calculo.valorDesconto)}`,
            180,
            y,
            {
                align: "right"
            }
        );


        y += 10;

    }


    /* =====================================================
       TOTAL
    ===================================================== */

    doc.setFontSize(14);


    doc.setTextColor(
        0,
        0,
        0
    );


    doc.setFont(
        "helvetica",
        "bold"
    );


    doc.text(
        `TOTAL: ${formatarMoedaPDF(calculo.total)}`,
        180,
        y,
        {
            align: "right"
        }
    );


    /* =====================================================
       SALVAR
    ===================================================== */

    const nomeArquivo =
        nome
            .replace(
                /[^a-zA-Z0-9À-ÿ ]/g,
                ""
            )
            .trim()
            .replace(
                /\s+/g,
                "_"
            );


    doc.save(
        `Orcamento-${nomeArquivo || "Hydra"}.pdf`
    );

}


/* =========================================================
   CARREGAR LOGO PARA O PDF
========================================================= */

async function carregarLogoBase64(url) {

    const resposta =
        await fetch(url);


    if (!resposta.ok) {

        throw new Error(
            "Erro ao carregar logo."
        );

    }


    const blob =
        await resposta.blob();


    return new Promise(
        (resolve, reject) => {

            const leitor =
                new FileReader();


            leitor.onloadend =
                () => resolve(
                    leitor.result
                );


            leitor.onerror =
                reject;


            leitor.readAsDataURL(
                blob
            );

        }
    );

}


/* =========================================================
   FORMATAÇÃO DE VALORES
========================================================= */

function formatarMoeda(valor) {

    return valor.toLocaleString(
        "pt-BR",
        {
            style: "currency",
            currency: "BRL"
        }
    );

}


function formatarMoedaPDF(valor) {

    return `R$ ${valor.toLocaleString(
        "pt-BR",
        {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }
    )}`;

}


/* =========================================================
   INICIALIZAÇÃO DO GERADOR
========================================================= */

carregarProdutos();