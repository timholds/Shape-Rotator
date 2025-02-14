'use client';

import React, { useState } from 'react';
import FeedbackButtons from '@/components/FeedbackButtons';

type GenerationStep = 'idle' | 'generating-code' | 'rendering-video' | 'completed';

export function ManimInterface() {
  const [userPrompt, setUserPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [generatedCode, setGeneratedCode] = useState('');
  const [videoUrl, setVideoUrl] = useState('');
  const [error, setError] = useState('');
  const [currentStep, setCurrentStep] = useState<GenerationStep>('idle');
  const [currentGenerationId, setCurrentGenerationId] = useState<string | null>(null);

  const API_BASE = process.env.NODE_ENV === 'production' 
    ? `https://${window.location.hostname}` 
    : 'http://localhost:8000';
    
  const getProgressPercentage = (step: GenerationStep) => {
    switch (step) {
      case 'idle': return 0;
      case 'generating-code': return 33;
      case 'rendering-video': return 66;
      case 'completed': return 100;
      default: return 0;
    }
  };

  const getProgressText = (step: GenerationStep) => {
    switch (step) {
      case 'idle': return 'Ready to generate';
      case 'generating-code': return 'Generating Manim code...';
      case 'rendering-video': return 'Rendering animation...';
      case 'completed': return 'Generation complete!';
      default: return '';
    }
  };

  const handleFeedback = (isPositive: boolean) => {
    console.log(`Feedback received: ${isPositive ? 'positive' : 'negative'} for generation ${currentGenerationId}`);
  };

  const pollStatus = async (taskId: string) => {
    const response = await fetch(`${API_BASE}/status/${taskId}`);
    if (!response.ok) throw new Error('Failed to get generation status');
    const status = await response.json();
    
    // Update code and generation step based on status
    if (status.code && !generatedCode) {
      setGeneratedCode(status.code);
      setCurrentStep('rendering-video');
    }
    
    return status;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setVideoUrl('');
    setGeneratedCode('');
    setCurrentStep('generating-code');
    setCurrentGenerationId(null);

    try {
      const response = await fetch(`${API_BASE}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          prompt: userPrompt,
          options: {
            quality: "low",
            resolution: "720p"
          }
        }),
      });

      if (!response.ok) throw new Error('Failed to start generation');
      const { task_id } = await response.json();
      
      console.log('Received task_id:', task_id); // Debug log
      setCurrentGenerationId(task_id);

      while (true) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        const status = await pollStatus(task_id);
        
        if (status.status === 'completed' && status.video_url) {
          setVideoUrl(`${API_BASE}${status.video_url}`);
          setCurrentStep('completed');
          break;
        } else if (status.status === 'failed') {
          throw new Error(status.error || 'Generation failed');
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate animation');
      console.error('Error:', err);
      setCurrentStep('idle');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-4">
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-2xl font-bold mb-4">Manim Animation Generator</h1>
        
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
          <button 
            type="submit" 
            disabled={isLoading || !userPrompt.trim()}
            className="w-full bg-blue-500 text-white p-2 rounded-md hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Generating...' : 'Generate Animation'}
          </button>
        </form>

        {error && (
          <div className="mt-4 p-4 bg-red-50 text-red-600 rounded-md">
            {error}
          </div>
        )}

        {isLoading && (
          <div className="mt-6 space-y-2">
            <div className="flex justify-between text-sm text-gray-600">
              <span>{getProgressText(currentStep)}</span>
              <span>{getProgressPercentage(currentStep)}%</span>
            </div>
            <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className="h-full bg-blue-500 transition-all duration-500 ease-in-out"
                style={{ width: `${getProgressPercentage(currentStep)}%` }}
              />
            </div>
          </div>
        )}

        {videoUrl && (
          <div className="mt-6">
            <h3 className="font-semibold mb-2">Generated Animation:</h3>
            <div className="relative w-full pt-[56.25%] bg-gray-100 rounded-md">
              <video
                key={videoUrl}
                src={videoUrl}
                controls
                className="absolute top-0 left-0 w-full h-full rounded-md"
              />
            </div>
            <div className="mt-4">
              {currentGenerationId && (
                <FeedbackButtons 
                  taskId={currentGenerationId}
                  onFeedback={handleFeedback}
                />
              )}
            </div>
          </div>
        )}

        {generatedCode && (
          <div className="mt-6">
            <h3 className="font-semibold mb-2">Generated Manim Code:</h3>
            <pre className="bg-gray-100 p-4 rounded-md overflow-x-auto text-sm">
              <code>{generatedCode}</code>
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}