from statistics import stdev, median
import json
import re
import random
import time
import numpy

# SEED = 873654221


def makespan(instancia, solucao):
    nM = len(instancia)
    tempo = [0] * nM

    tarefa = [0] * len(solucao)

    for t in solucao:
        if tarefa[t-1] == 1:
            return "SOLUÇÃO INVÁLIDA: tarefa repetida!"
        else:
            tarefa[t-1] = 1

        for m in range(nM):
            if tempo[m] < tempo[m-1] and m != 0:
                tempo[m] = tempo[m-1]

            tempo[m] += instancia[m][t-1]

    return tempo[nM-1]


def lerInstancias(listaArquivos):
    jobs = []
    for file in listaArquivos:
        f = open(file, "r")
        job = f.read()
        job = job[job.index("processing times :") +
                  19: job.index("\nnumber of jobs")].split("\n")
        job = list(map(lambda list: [int(i)
                   for i in re.split(r"\s+", list.strip())], job))

        jobs.append(job)
    return jobs


def criarPopulacaoInicial(instancia, tamanho):
    permutation = []

    nlist = list(range(1, len(instancia[0])))
    for _ in range(tamanho):
        random.shuffle(nlist)
        permutation.append(nlist.copy())

    return permutation


def avaliarPop(populacao):
    result = []
    for solucao in populacao:
        result.append(makespan(instancia, solucao))

    return result


def retornaMelhorSolucao(populacao, aptidaoPop):
    return {
        'solucao': populacao[aptidaoPop.index(min(aptidaoPop))],
        'aptidao': min(aptidaoPop),
        'tempoFinal': 0
    }


def selecionarPop(populacao, aptidaoPop):
    conj = list(zip(populacao, aptidaoPop))
    conj.sort(key=lambda t: t[1])
    # [0:(len(populacao) * 0.5).__floor__() or 1]]
    return [list(i)[0] for i in conj]


def recombinacao(populacaoSelecionada):
    for pop in populacaoSelecionada * 2:
        inicio = random.randint(0, len(pop))
        fim = inicio + (len(pop) * 0.33).__floor__()

        if (inicio > fim):
            inicio, fim = fim, inicio

        pop[inicio:fim] = numpy.roll(pop[inicio:fim], random.randint(1, 3))

    return populacaoSelecionada


def mutacao(novasSolucoes):
    for array in novasSolucoes:
        while True:
            if (random.random() < 0.05):
                pos = random.randint(1, len(array) - 1)
                array[pos], array[len(
                    array) - pos] = array[len(array) - pos], array[pos]
            else:
                break

    return novasSolucoes


def selecionarNovaGeracao(populacaoAtual, novasSolucoes):
    newGen = (populacaoAtual + novasSolucoes)
    random.shuffle(newGen)
    return newGen[0: ((len(newGen) * 0.5).__floor__() or 1)]


def salvarRelatorio(relatorios):
    f = open('result.json', 'a+')

    for relatorio in relatorios:
        apt, tempo, solucoes = [], [], []

        for i in range(len(relatorio)):
            apt.append(relatorio[i]['aptidao'])
            tempo.append(relatorio[i]['tempoFinal'])
            solucoes.append(relatorio[i]['solucao'])

        # print(apt, tempo)
        data = {
            "job": files[relatorios.index(relatorio)],
            "order": str(sorted(list(zip(apt, solucoes)), key=lambda t: t[0])[0][1]),
            "lower": min(apt),
            "upper": max(apt),
            "mdApt": median(apt),
            "desApt": stdev(apt),
            "mdTime": median(tempo),
            "desTime": stdev(tempo),
        }

        f.write(json.dumps(data, indent=4) + ",\n")


files = list(numpy.repeat([
    "tai20_5.txt",
    "tai20_10.txt",
    "tai20_20.txt",
    "tai50_5.txt",
    "tai50_10.txt",
    "tai50_20.txt",
    "tai100_5.txt",
    "tai100_10.txt",
    "tai100_20.txt",
    "tai200_10.txt",
], 5))

listaInstancias = lerInstancias(files)
relatorio = [dict() for _ in listaInstancias]

for instancia in listaInstancias:
    melhoresSolucoes = {}
    tamanhoPop = len(instancia) * 2
    tempoMaximo = 10

    for it in range(10):
        melhorSolucao = {
            'solucao': [],
            'aptidao': 9223372036854775807,
            'tempoFinal': 0,
        }
        tempoInicial = time.time()
        populacao = criarPopulacaoInicial(instancia, tamanhoPop)

        i = 0
        while True:
            if tempoMaximo <= time.time() - tempoInicial:
                break

            aptidaoPop = avaliarPop(populacao)
            melhorSolucaoAtual = retornaMelhorSolucao(populacao, aptidaoPop)
            i -=- 1

            if melhorSolucao['aptidao'] > melhorSolucaoAtual['aptidao']:
                i = 0
                melhorSolucao = melhorSolucaoAtual

            populacaoSelecionada = selecionarPop(populacao, aptidaoPop)
            novasSolucoes = recombinacao(populacaoSelecionada)
            novasSolucoes = mutacao(novasSolucoes)
            populacao = selecionarNovaGeracao(populacao, novasSolucoes)

            if i > 100:
                break

        melhorSolucao['tempoFinal'] = time.time() - tempoInicial
        melhoresSolucoes[it] = melhorSolucao
    relatorio[relatorio.index({})] = melhoresSolucoes

salvarRelatorio(relatorio)