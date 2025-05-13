#include <stdio.h>
#include <stdlib.h>

typedef struct no No;

struct no {
    No *esq;
    int dado;
    No *dir;
};


No *criar_no(int dado) {
    No *novo_no = malloc(sizeof(No));
    if (novo_no) {
        novo_no->esq = NULL;
        novo_no->dir = NULL;
        novo_no->dado = dado;
    }
    
    return novo_no;
}


void exibir(No *no) {
    if (no) { // no is not NULL
        exibir(no->dir);
        printf("(%d)\n", no->dado); // em-ordem
        exibir(no->esq);
        printf("(%d)", no->dado);
    }
}


int main() {
    No *raiz = criar_no(1);
    raiz->esq = criar_no(2);
    raiz->esq->esq = criar_no(4);
    raiz->esq->dir = criar_no(5);
    raiz->dir = criar_no(3);
    raiz->dir->esq = criar_no(6);
    raiz->dir->dir = criar_no(7);
    exibir(raiz);
    
    return 0;
}