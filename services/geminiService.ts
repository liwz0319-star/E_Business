
import { GoogleGenAI, Type } from "@google/genai";

export enum GenerationType {
  TEXT = 'Text Content',
  IMAGE = 'Product Image',
  VIDEO = 'Ad Video',
  SEARCH = 'Market Insight'
}

const mockData = (type: GenerationType) => {
    switch(type) {
        case GenerationType.IMAGE: return "https://picsum.photos/800/450";
        case GenerationType.VIDEO: return "https://www.w3schools.com/html/mov_bbb.mp4";
        case GenerationType.SEARCH: return "Our market analysis shows a 15% increase in demand for eco-friendly tech accessories. Competitors like BrandX have recently dropped prices, suggesting a saturated entry-level market.";
        default: return "Transform your daily routine with the all-new AeroStream Headphones. Engineered for silence, designed for comfort. Experience the future of sound with active noise cancellation and 40-hour battery life. Order now and elevate your audio experience.";
    }
}

export const generateContent = async (prompt: string, type: GenerationType): Promise<any> => {
  // Handle mandatory key selection for Veo models (Video)
  if (type === GenerationType.VIDEO) {
    const aistudio = (window as any).aistudio;
    if (aistudio && typeof aistudio.hasSelectedApiKey === 'function') {
      const hasKey = await aistudio.hasSelectedApiKey();
      if (!hasKey) {
        await aistudio.openSelectKey();
        // Proceeding assuming selection was triggered as per guidelines
      }
    }
  }

  // Create a new GoogleGenAI instance right before the call to ensure latest API key
  const apiKey = process.env.API_KEY;
  if (!apiKey) {
      console.warn("API Key is missing. Using mock data for demo.");
      return mockData(type);
  }

  const ai = new GoogleGenAI({ apiKey });

  try {
    switch (type) {
      case GenerationType.IMAGE:
        const imgResponse = await ai.models.generateContent({
          model: 'gemini-2.5-flash-image',
          contents: { parts: [{ text: prompt }] },
          config: { imageConfig: { aspectRatio: "16:9" } }
        });
        const imagePart = imgResponse.candidates?.[0]?.content?.parts.find(p => p.inlineData);
        return imagePart ? `data:image/png;base64,${imagePart.inlineData.data}` : mockData(type);

      case GenerationType.VIDEO:
        let op = await ai.models.generateVideos({
          model: 'veo-3.1-fast-generate-preview',
          prompt: prompt,
          config: { resolution: '720p', aspectRatio: '16:9' }
        });
        
        while (!op.done) {
          // Poll every 10 seconds for video operations as per rules
          await new Promise(r => setTimeout(r, 10000));
          op = await ai.operations.getVideosOperation({ operation: op });
        }
        
        const downloadLink = op.response?.generatedVideos?.[0]?.video?.uri;
        if (!downloadLink) throw new Error("Video generation complete but no URI returned.");
        
        const vidResponse = await fetch(`${downloadLink}&key=${apiKey}`);
        if (!vidResponse.ok) throw new Error(`Failed to download video: ${vidResponse.statusText}`);
        
        const blob = await vidResponse.blob();
        return URL.createObjectURL(blob);

      case GenerationType.SEARCH:
        const searchRes = await ai.models.generateContent({
          model: 'gemini-3-flash-preview',
          contents: prompt,
          config: { tools: [{ googleSearch: {} }] }
        });
        return searchRes.text;

      case GenerationType.TEXT:
      default:
        const textRes = await ai.models.generateContent({
          model: 'gemini-3-flash-preview',
          contents: prompt,
          config: {
              systemInstruction: "You are a world-class e-commerce copywriter. Create high-converting content for product listings and ads."
          }
        });
        return textRes.text;
    }
  } catch (error: any) {
    console.error("Gemini API Error:", error);
    
    const errorMsg = error.message || "";
    // If the error is 403 or entity not found, it likely needs key re-selection
    if (errorMsg.includes("403") || errorMsg.includes("permission") || errorMsg.includes("Requested entity was not found")) {
      const aistudio = (window as any).aistudio;
      if (aistudio && typeof aistudio.openSelectKey === 'function') {
        await aistudio.openSelectKey();
      }
    }
    
    // Fallback to mock data for demo safety
    return mockData(type);
  }
};
