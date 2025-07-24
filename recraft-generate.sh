#!/bin/bash

# Recraft Image Generation Shell Script
# Author: Claude
# Date: 2025-04-18

# Default values with embedded API key
API_KEY="hc0nEDHQNbu1PCASCPcHvBc1ZxYTWD21Misj8qzRsCKYLMjc8tWwrNzAnsK5U6XO"
PROMPT=""
SIZE="1024x1024"
NUM_IMAGES=1
OUTPUT_DIR="./generated_images"
SAVE_IMAGE=true

# Display help
show_help() {
    echo "Recraft Image Generation Shell Script"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -k, --key API_KEY       Recraft API key (default is already set)"
    echo "  -p, --prompt PROMPT     Image generation prompt (required)"
    echo "  -s, --size SIZE         Image size (default: 1024x1024)"
    echo "                          Options: 1024x1024, 1024x1792, 1792x1024"
    echo "  -n, --num NUM           Number of images to generate (default: 1)"
    echo "  -o, --output DIR        Output directory for images (default: ./generated_images)"
    echo "  -j, --json-only         Output only JSON response, don't save images"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Example:"
    echo "  $0 -p \"A beautiful sunset over the ocean\" -s 1024x1792 -n 2"
    echo ""
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -k|--key)
            API_KEY="$2"
            shift 2
            ;;
        -p|--prompt)
            PROMPT="$2"
            shift 2
            ;;
        -s|--size)
            SIZE="$2"
            shift 2
            ;;
        -n|--num)
            NUM_IMAGES="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -j|--json-only)
            SAVE_IMAGE=false
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Check if prompt is provided
if [ -z "$PROMPT" ]; then
    echo "Error: Prompt not provided"
    echo "Please provide a prompt with -p option"
    exit 1
fi

# Validate size
if [[ "$SIZE" != "1024x1024" && "$SIZE" != "1024x1792" && "$SIZE" != "1792x1024" ]]; then
    echo "Error: Invalid size '$SIZE'"
    echo "Valid options: 1024x1024, 1024x1792, 1792x1024"
    exit 1
fi

# Create JSON payload
JSON_PAYLOAD=$(cat <<EOF
{
  "prompt": "$PROMPT",
  "n": $NUM_IMAGES,
  "size": "$SIZE"
}
EOF
)

# Make API request
echo "Generating image with prompt: '$PROMPT'"
echo "Size: $SIZE, Number of images: $NUM_IMAGES"

RESPONSE=$(curl -s -X POST "https://external.api.recraft.ai/v1/images/generations" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $API_KEY" \
    -d "$JSON_PAYLOAD")

# Check if there was an error in the API response
if [[ $RESPONSE == *"error"* ]]; then
    echo "Error from Recraft API:"
    echo "$RESPONSE" | jq .
    exit 1
fi

# If json-only flag is set, just output the JSON response
if [ "$SAVE_IMAGE" = false ]; then
    echo "$RESPONSE" | jq .
    exit 0
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Extract image URLs and IDs
IMAGE_URLS=$(echo "$RESPONSE" | jq -r '.data[].url')
IMAGE_IDS=$(echo "$RESPONSE" | jq -r '.data[].image_id')

# Mac-friendly way to handle arrays
urls=()
ids=()
while IFS= read -r line; do
    urls+=("$line")
done <<< "$IMAGE_URLS"

while IFS= read -r line; do
    ids+=("$line")
done <<< "$IMAGE_IDS"

# Download images
echo ""
echo "Downloading generated images to $OUTPUT_DIR/"

for i in "${!urls[@]}"; do
    URL="${urls[$i]}"
    ID="${ids[$i]}"
    
    # Clean up URL
    URL=$(echo "$URL" | tr -d '\r\n')
    
    # Create a timestamp
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    
    # Create filename
    FILENAME="${OUTPUT_DIR}/recraft_${TIMESTAMP}_${i}_${ID}.png"
    
    echo "Downloading image $((i+1))/${#urls[@]} to $FILENAME"
    
    # Download image
    curl -s "$URL" -o "$FILENAME"
    
    # Check if download was successful
    if [ $? -eq 0 ]; then
        echo "✅ Image $((i+1)) downloaded successfully"
    else
        echo "❌ Failed to download image $((i+1))"
    fi
done

echo ""
echo "Generation complete!"
echo "JSON response saved to ${OUTPUT_DIR}/response.json"

# Save full JSON response for reference
echo "$RESPONSE" > "${OUTPUT_DIR}/response.json"

echo ""
echo "To view your images:"
echo "open $OUTPUT_DIR"

# End of script