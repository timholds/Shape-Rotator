import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';

const ManimInterface = () => {
  const [userPrompt, setUserPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [generatedCode, setGeneratedCode] = useState('');
  const [videoUrl, setVideoUrl] = useState('');
  const [error, setError] = useState('');

  const API_BASE = 'http://localhost:8000';
  
  // Function to poll generation status
  const pollStatus = async (taskId) => {
    const response = await fetch(`${API_BASE}/status/${taskId}`);
    if (!response.ok) throw new Error('Failed to get generation status');
    return response.json();
  };

  // Function to start generation and poll for results
  const generateAnimation = async (prompt) => {
    // Start generation
    const response = await fetch(`${API_BASE}/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt }),
    });

    if (!response.ok) throw new Error('Failed to start generation');
    const { task_id, code } = await response.json();
    
    // Return initial code
    return { taskId: task_id, code };
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setVideoUrl('');

    try {
      // Generate Manim code using the placeholder LLM function
      const code = await generateManimCode(userPrompt);
      setGeneratedCode(code);

      // Placeholder for video generation API call
      // This would be replaced with actual backend integration
      await new Promise(resolve => setTimeout(resolve, 2000));
      setVideoUrl('/api/placeholder/640/360');

    } catch (err) {
      setError('Failed to generate animation. Please try again.');
      console.error('Error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-4 space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Manim Animation Generator</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <textarea
                value={userPrompt}
                onChange={(e) => setUserPrompt(e.target.value)}
                placeholder="Describe the animation you want to create..."
                className="w-full h-32 p-2 border rounded-md"
                required
              />
            </div>
            <Button 
              type="submit" 
              disabled={isLoading || !userPrompt.trim()}
              className="w-full"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Generating Animation...
                </>
              ) : (
                'Generate Animation'
              )}
            </Button>
          </form>

          {error && (
            <div className="mt-4 p-4 bg-red-50 text-red-600 rounded-md">
              {error}
            </div>
          )}

          {generatedCode && (
            <div className="mt-4">
              <h3 className="font-semibold mb-2">Generated Manim Code:</h3>
              <pre className="bg-gray-100 p-4 rounded-md overflow-x-auto">
                <code>{generatedCode}</code>
              </pre>
            </div>
          )}

          {videoUrl && (
            <div className="mt-4">
              <h3 className="font-semibold mb-2">Generated Animation:</h3>
              <div className="relative w-full pt-[56.25%]">
                <img
                  src={videoUrl}
                  alt="Generated animation"
                  className="absolute top-0 left-0 w-full h-full object-cover rounded-md"
                />
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default ManimInterface;