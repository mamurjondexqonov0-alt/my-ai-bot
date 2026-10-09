#!/bin/bash

RENDER_API_KEY="rnd_AzCV1Ueb6vLjm6ZliwI8fXTcs5oc"

echo "1. Git ga o'zgarishlar qo'shilmoqda..."
git add .
git commit -m "Avtomatik yangilanish va o'rganish"
git push

echo "2. Render API orqali Service ID topilmoqda..."
# Render'dagi barcha servicelarni olib, birinchisining ID sini avtomatik olamiz
RESPONSE=$(curl -s -X GET "https://api.render.com/v1/services?limit=1" \
     -H "Authorization: Bearer $RENDER_API_KEY")

SERVICE_ID=$(echo "$RESPONSE" | grep -o '"id":"srv-[^"]*' | head -n 1 | cut -d'"' -f4)

if [ -z "$SERVICE_ID" ]; then
    echo "❌ Xatolik: Service ID topilmadi! API kalitni tekshiring."
    exit 1
fi

echo "✅ Topilgan Service ID: $SERVICE_ID"

echo "3. Server qayta yuklanmoqda (Redeploy)..."
curl -s -X POST "https://api.render.com/v1/services/$SERVICE_ID/deploys" \
     -H "Authorization: Bearer $RENDER_API_KEY" \
     -H "Content-Type: application/json" > /dev/null

echo -e "\n🎉 Bajarildi! Render serveri avtomatik ravishda yangilanmoqda."
