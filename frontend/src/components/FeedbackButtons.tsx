import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown } from 'lucide-react';

const FeedbackButtons = ({ onFeedback, generationId }) => {
  const [feedback, setFeedback] = useState(null);
  const [showFeedbackAlert, setShowFeedbackAlert] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleFeedback = async (isPositive) => {
    if (isSubmitting) return;
    setIsSubmitting(true);
    
    try {
      const response = await fetch('http://localhost:8000/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          generation_id: generationId,
          is_positive: isPositive,
        }),
      });

      if (!response.ok) throw new Error('Failed to submit feedback');
      
      setShowFeedbackAlert(true);
      setTimeout(() => setShowFeedbackAlert(false), 3000);
      
      setFeedback(isPositive);
      onFeedback?.(isPositive);
    } catch (error) {
      console.error('Error submitting feedback:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="relative">
      <div className="flex items-center gap-4 mt-2">
        <span className="text-sm text-gray-600">Was this animation helpful?</span>
        <button
          onClick={() => handleFeedback(true)}
          disabled={feedback !== null || isSubmitting}
          className={`p-2 rounded-full transition-colors ${
            feedback === true
              ? 'bg-green-100 text-green-600'
              : 'hover:bg-gray-100 text-gray-500'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
          aria-label="Thumbs up"
        >
          <ThumbsUp size={20} />
        </button>
        <button
          onClick={() => handleFeedback(false)}
          disabled={feedback !== null || isSubmitting}
          className={`p-2 rounded-full transition-colors ${
            feedback === false
              ? 'bg-red-100 text-red-600'
              : 'hover:bg-gray-100 text-gray-500'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
          aria-label="Thumbs down"
        >
          <ThumbsDown size={20} />
        </button>
        {feedback !== null && (
          <span className="text-sm text-gray-600">Thanks for your feedback!</span>
        )}
      </div>
      
      {showFeedbackAlert && (
        <div className="absolute bottom-4 right-4 bg-green-100 text-green-800 px-4 py-2 rounded-md shadow-md">
          Feedback submitted successfully!
        </div>
      )}
    </div>
  );
};

export default FeedbackButtons;