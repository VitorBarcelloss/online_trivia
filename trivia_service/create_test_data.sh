#!/bin/bash

BASE_URL="http://localhost:8001"
PLAYER_ID="11111111-1111-1111-1111-111111111111"
PACKAGE_ID=1

create_question() {
    local statement="$1"
    local explanation="$2"

    response=$(curl -s -X POST \
        "$BASE_URL/questions?player_id=$PLAYER_ID" \
        -H "Content-Type: application/json" \
        -d "{
            \"package_id\": $PACKAGE_ID,
            \"statement\": \"$statement\",
            \"explanation\": \"$explanation\"
        }")

    echo "$response"
    echo "$response" | python -c "import sys,json; print(json.load(sys.stdin)['id'])"
}

create_alternative() {
    local question_id="$1"
    local text="$2"
    local is_correct="$3"

    curl -s -X POST \
        "$BASE_URL/alternatives?player_id=$PLAYER_ID" \
        -H "Content-Type: application/json" \
        -d "{
            \"question_id\": $question_id,
            \"text\": \"$text\",
            \"is_correct\": $is_correct
        }"

    echo
}

echo "Criando pergunta 2..."
q=$(create_question \
    "Qual é o maior planeta do Sistema Solar?" \
    "Júpiter é o maior planeta do Sistema Solar.")
q_id=$(echo "$q" | tail -1)

create_alternative "$q_id" "Júpiter" true
create_alternative "$q_id" "Saturno" false
create_alternative "$q_id" "Netuno" false
create_alternative "$q_id" "Terra" false


echo "Criando pergunta 3..."
q=$(create_question \
    "Quantos continentes existem tradicionalmente?" \
    "A divisão tradicional considera seis continentes.")
q_id=$(echo "$q" | tail -1)

create_alternative "$q_id" "Seis" true
create_alternative "$q_id" "Quatro" false
create_alternative "$q_id" "Cinco" false
create_alternative "$q_id" "Oito" false


echo "Criando pergunta 4..."
q=$(create_question \
    "Qual é o maior oceano da Terra?" \
    "O Oceano Pacífico é o maior oceano da Terra.")
q_id=$(echo "$q" | tail -1)

create_alternative "$q_id" "Oceano Pacífico" true
create_alternative "$q_id" "Oceano Atlântico" false
create_alternative "$q_id" "Oceano Índico" false
create_alternative "$q_id" "Oceano Ártico" false


echo "Criando pergunta 5..."
q=$(create_question \
    "Quem escreveu Dom Casmurro?" \
    "Dom Casmurro foi escrito por Machado de Assis.")
q_id=$(echo "$q" | tail -1)

create_alternative "$q_id" "Machado de Assis" true
create_alternative "$q_id" "José de Alencar" false
create_alternative "$q_id" "Carlos Drummond de Andrade" false
create_alternative "$q_id" "Monteiro Lobato" false


echo "Criando pergunta 6..."
q=$(create_question \
    "Qual é o resultado de 8 vezes 7?" \
    "8 multiplicado por 7 é igual a 56.")
q_id=$(echo "$q" | tail -1)

create_alternative "$q_id" "56" true
create_alternative "$q_id" "48" false
create_alternative "$q_id" "64" false
create_alternative "$q_id" "54" false


echo "Criando pergunta 7..."
q=$(create_question \
    "Qual animal é conhecido como rei da selva?" \
    "O leão é tradicionalmente conhecido como rei da selva.")
q_id=$(echo "$q" | tail -1)

create_alternative "$q_id" "Leão" true
create_alternative "$q_id" "Tigre" false
create_alternative "$q_id" "Elefante" false
create_alternative "$q_id" "Gorila" false


echo "Criando pergunta 8..."
q=$(create_question \
    "Qual é o idioma oficial do Brasil?" \
    "O português é o idioma oficial do Brasil.")
q_id=$(echo "$q" | tail -1)

create_alternative "$q_id" "Português" true
create_alternative "$q_id" "Espanhol" false
create_alternative "$q_id" "Inglês" false
create_alternative "$q_id" "Francês" false


echo "Criando pergunta 9..."
q=$(create_question \
    "Qual planeta é conhecido como planeta vermelho?" \
    "Marte possui uma aparência avermelhada devido à presença de óxidos de ferro.")
q_id=$(echo "$q" | tail -1)

create_alternative "$q_id" "Marte" true
create_alternative "$q_id" "Vênus" false
create_alternative "$q_id" "Mercúrio" false
create_alternative "$q_id" "Saturno" false


echo "Criando pergunta 10..."
q=$(create_question \
    "Qual é o símbolo químico da água?" \
    "A água é representada pela fórmula H2O.")
q_id=$(echo "$q" | tail -1)

create_alternative "$q_id" "H2O" true
create_alternative "$q_id" "CO2" false
create_alternative "$q_id" "O2" false
create_alternative "$q_id" "NaCl" false


echo
echo "======================================"
echo "Dados de teste criados!"
echo "Package ID: $PACKAGE_ID"
echo "======================================"


3KSNCY