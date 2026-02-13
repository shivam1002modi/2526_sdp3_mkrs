export const dummyChatResponse = [
    {
        custom: {
            text: "Based on my analysis of the document, this PDF covers the key principles of machine learning and artificial intelligence. The document is organized into several chapters covering supervised learning, neural networks, and practical applications. Would you like me to elaborate on any specific section?",
            sources: [
                {
                    url: "#",
                    title: "AI & ML Fundamentals",
                    page: 12
                }
            ]
        }
    }
];

export const dummyUploadResponse = {
    filename: "knowledge_base_update.pdf",
    message: "File uploaded successfully."
};

// Generator for retraining logs
export async function* dummyRetrainGenerator() {
    const steps = [
        "Connecting to training service...",
        "Loading knowledge base documents...",
        "Vectorizing documents [████████████████████] 100%",
        "Updating model weights...",
        "Optimizing context window...",
        "Validating model accuracy...",
        "✅ Retraining completed successfully!"
    ];

    for (const step of steps) {
        await new Promise(resolve => setTimeout(resolve, 800));
        yield step + "\n";
    }
}
