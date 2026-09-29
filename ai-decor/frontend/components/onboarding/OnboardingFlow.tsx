'use client';

import { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Separator } from '@/components/ui/separator';
import { 
  Upload, 
  Image as ImageIcon, 
  Check, 
  ArrowRight,
  Sparkles,
  Home,
  Palette,
  Heart
} from 'lucide-react';

interface OnboardingData {
  image: File | null;
  roomType: string;
  style: string;
  budget: string;
  timeline: string;
  colors: string[];
  goals: string[];
}

interface OnboardingFlowProps {
  onComplete: (data: OnboardingData) => void;
  onSkip: () => void;
}

const roomTypes = [
  'Living Room', 'Bedroom', 'Kitchen', 'Bathroom', 'Dining Room', 
  'Home Office', 'Nursery', 'Basement', 'Attic', 'Other'
];

const styles = [
  'Modern', 'Traditional', 'Contemporary', 'Minimalist', 'Scandinavian',
  'Industrial', 'Bohemian', 'Farmhouse', 'Mid-Century', 'Rustic'
];

const budgets = [
  'Under $1,000', '$1,000 - $5,000', '$5,000 - $10,000', 
  '$10,000 - $25,000', '$25,000+'
];

const timelines = [
  'ASAP', 'Within 1 month', '1-3 months', '3-6 months', '6+ months'
];

const colorOptions = [
  'Neutral (White, Gray, Beige)', 'Blue', 'Green', 'Warm (Red, Orange, Yellow)',
  'Cool (Purple, Pink)', 'Earth Tones', 'Black & White', 'Pastels'
];

const goalOptions = [
  'Make it more functional', 'Improve storage', 'Better lighting',
  'More comfortable', 'Increase home value', 'Better for entertaining',
  'More relaxing', 'Better for work/study'
];

export default function OnboardingFlow({ onComplete, onSkip }: OnboardingFlowProps) {
  const [step, setStep] = useState(1);
  const [data, setData] = useState<OnboardingData>({
    image: null,
    roomType: '',
    style: '',
    budget: '',
    timeline: '',
    colors: [],
    goals: []
  });

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (files) => {
      if (files.length > 0) {
        setData(prev => ({ ...prev, image: files[0] }));
      }
    },
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.webp']
    },
    multiple: false
  });

  const handleNext = () => {
    if (step < 4) {
      setStep(step + 1);
    } else {
      onComplete(data);
    }
  }
  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  const toggleArrayItem = (array: string[], item: string) => {
    return array.includes(item) 
      ? array.filter(i => i !== item)
      : [...array, item];
  };

  const updateData = (key: keyof OnboardingData, value: OnboardingData[keyof OnboardingData]) => {
    setData(prev => ({ ...prev, [key]: value }));
  };

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <div className="text-center space-y-6">
            <div className="mx-auto w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mb-4">
              <Sparkles className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900">
              Welcome to Your Design Session! 🎨
            </h2>
            <p className="text-gray-600 max-w-md mx-auto">
              I&apos;m your personal AI interior designer. Let&apos;s create something amazing together! 
              First, I&apos;d love to see your space.
            </p>
            <div className="text-sm text-gray-500">
              Step 1 of 4
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Upload a Photo of Your Room
              </h2>
              <p className="text-gray-600">
                This helps me understand your current space and provide better suggestions.
              </p>
            </div>
            
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                isDragActive 
                  ? 'border-blue-500 bg-blue-50' 
                  : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              <input {...getInputProps()} />
              {data.image ? (
                <div className="space-y-2">
                  <Check className="w-8 h-8 text-green-500 mx-auto" />
                  <p className="text-green-600 font-medium">{data.image.name}</p>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      setData(prev => ({ ...prev, image: null }));
                    }}
                  >
                    Change Image
                  </Button>
                </div>
              ) : (
                <div className="space-y-2">
                  <Upload className="w-8 h-8 text-gray-400 mx-auto" />
                  <p className="text-gray-600">
                    {isDragActive 
                      ? 'Drop your image here...' 
                      : 'Drag & drop an image of your room, or click to select'
                    }
                  </p>
                  <p className="text-sm text-gray-500">
                    Supports JPG, PNG, GIF, WebP
                  </p>
                </div>
              )}
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Tell Me About Your Space
              </h2>
              <p className="text-gray-600">
                Help me understand your preferences and goals.
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  What type of room is this? *
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {roomTypes.map((type) => (
                    <Button
                      key={type}
                      variant={data.roomType === type ? "default" : "outline"}
                      size="sm"
                      onClick={() => updateData('roomType', type)}
                      className="justify-start"
                    >
                      <Home className="w-4 h-4 mr-2" />
                      {type}
                    </Button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  What style appeals to you? *
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {styles.map((style) => (
                    <Button
                      key={style}
                      variant={data.style === style ? "default" : "outline"}
                      size="sm"
                      onClick={() => updateData('style', style)}
                      className="justify-start"
                    >
                      <Palette className="w-4 h-4 mr-2" />
                      {style}
                    </Button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Budget Range
                  </label>
                  <select 
                    value={data.budget}
                    onChange={(e) => updateData('budget', e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-md"
                  >
                    <option value="">Select budget</option>
                    {budgets.map((budget) => (
                      <option key={budget} value={budget}>{budget}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Timeline
                  </label>
                  <select 
                    value={data.timeline}
                    onChange={(e) => updateData('timeline', e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-md"
                  >
                    <option value="">Select timeline</option>
                    {timelines.map((timeline) => (
                      <option key={timeline} value={timeline}>{timeline}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Final Preferences
              </h2>
              <p className="text-gray-600">
                A few more details to personalize your experience.
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Color Preferences (select all that apply)
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {colorOptions.map((color) => (
                    <Button
                      key={color}
                      variant={data.colors.includes(color) ? "default" : "outline"}
                      size="sm"
                      onClick={() => updateData('colors', toggleArrayItem(data.colors, color))}
                      className="justify-start"
                    >
                      {data.colors.includes(color) && <Check className="w-4 h-4 mr-2" />}
                      {color}
                    </Button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  What are your main goals? (select all that apply)
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {goalOptions.map((goal) => (
                    <Button
                      key={goal}
                      variant={data.goals.includes(goal) ? "default" : "outline"}
                      size="sm"
                      onClick={() => updateData('goals', toggleArrayItem(data.goals, goal))}
                      className="justify-start"
                    >
                      {data.goals.includes(goal) && <Check className="w-4 h-4 mr-2" />}
                      <Heart className="w-4 h-4 mr-2" />
                      {goal}
                    </Button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl shadow-xl border-0">
        <CardHeader className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-t-lg">
          <CardTitle className="text-center text-2xl">
            {step === 1 ? 'Welcome!' : `Step ${step} of 4`}
          </CardTitle>
          <CardDescription className="text-center text-blue-100">
            {step === 1 ? 'Let&apos;s get started with your interior design journey' : 'Almost there!'}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6 pt-6">
          {renderStep()}
          
          <Separator className="my-6" />
          
          <div className="flex justify-between">
            <Button 
              variant="outline" 
              onClick={handleBack}
              disabled={step === 1}
              className="bg-white border-gray-300 hover:bg-gray-50"
            >
              Back
            </Button>
            
            <div className="flex space-x-2">
              <Button 
                variant="ghost" 
                onClick={onSkip}
                className="text-gray-600 hover:text-gray-900 hover:bg-gray-100"
              >
                Skip Setup
              </Button>
              <Button 
                onClick={handleNext}
                disabled={step === 2 && !data.image}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg"
              >
                {step === 4 ? 'Start Chatting!' : 'Next'}
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

