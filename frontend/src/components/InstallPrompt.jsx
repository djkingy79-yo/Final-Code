/* DO NOT UNDO — InstallPrompt component. All features in this file are approved and must be preserved. */
import { useState, useEffect } from 'react';
import { Button } from '../components/ui/button';
import { Download, X } from 'lucide-react';

const InstallPrompt = () => {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [showPrompt, setShowPrompt] = useState(false);
  const [isIOS, setIsIOS] = useState(false);
  const [showIOSInstructions, setShowIOSInstructions] = useState(false);

  useEffect(() => {
    // Check if already installed
    if (window.matchMedia('(display-mode: standalone)').matches) {
      return;
    }

    // Check if dismissed recently
    const dismissed = localStorage.getItem('pwa-prompt-dismissed');
    if (dismissed) {
      const dismissedTime = parseInt(dismissed);
      if (Date.now() - dismissedTime < 7 * 24 * 60 * 60 * 1000) {
        return;
      }
    }

    // Check for iOS
    const isIOSDevice = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    setIsIOS(isIOSDevice);

    if (isIOSDevice) {
      // Show iOS instructions after a delay
      setTimeout(() => setShowPrompt(true), 3000);
    } else {
      // Listen for beforeinstallprompt event
      const handler = (e) => {
        e.preventDefault();
        setDeferredPrompt(e);
        setTimeout(() => setShowPrompt(true), 3000);
      };

      window.addEventListener('beforeinstallprompt', handler);
      return () => window.removeEventListener('beforeinstallprompt', handler);
    }
  }, []);

  const handleInstall = async () => {
    if (isIOS) {
      setShowIOSInstructions(true);
      return;
    }

    if (!deferredPrompt) return;

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    
    if (outcome === 'accepted') {
      setShowPrompt(false);
    }
    setDeferredPrompt(null);
  };

  const handleDismiss = () => {
    setShowPrompt(false);
    setShowIOSInstructions(false);
    localStorage.setItem('pwa-prompt-dismissed', Date.now().toString());
  };

  if (!showPrompt) return null;

  if (showIOSInstructions) {
    return (
      <div className="fixed bottom-20 left-4 right-4 md:left-auto md:right-4 md:w-80 bg-slate-900 text-white rounded-xl shadow-2xl p-4 z-50 animate-in slide-in-from-bottom-4">
        <button 
          onClick={handleDismiss}
          className="absolute top-2 right-2 text-slate-400 hover:text-white"
        >
          <X className="w-5 h-5" />
        </button>
        <h3 className="font-semibold text-lg mb-3">Install on iOS</h3>
        <ol className="text-sm text-slate-300 space-y-2">
          <li className="flex items-start gap-2">
            <span className="bg-slate-700 rounded-full w-5 h-5 flex items-center justify-center text-xs shrink-0">1</span>
            <span>Tap the <strong>Share</strong> button at the bottom of Safari</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="bg-slate-700 rounded-full w-5 h-5 flex items-center justify-center text-xs shrink-0">2</span>
            <span>Scroll down and tap <strong>"Add to Home Screen"</strong></span>
          </li>
          <li className="flex items-start gap-2">
            <span className="bg-slate-700 rounded-full w-5 h-5 flex items-center justify-center text-xs shrink-0">3</span>
            <span>Tap <strong>"Add"</strong> in the top right corner</span>
          </li>
        </ol>
        <Button 
          variant="outline" 
          size="sm" 
          className="w-full mt-4 border-slate-600 text-white hover:bg-slate-800"
          onClick={handleDismiss}
        >
          Got it
        </Button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-20 left-4 right-4 md:left-auto md:right-4 md:w-80 bg-slate-900 text-white rounded-xl shadow-2xl p-4 z-50 animate-in slide-in-from-bottom-4">
      <button 
        onClick={handleDismiss}
        className="absolute top-2 right-2 text-slate-400 hover:text-white"
      >
        <X className="w-5 h-5" />
      </button>
      <div className="flex items-start gap-3">
        <div className="bg-gradient-to-br from-slate-700 to-slate-800 p-2 rounded-lg">
          <Download className="w-6 h-6 text-amber-400" />
        </div>
        <div className="flex-1">
          <h3 className="font-semibold">Install App</h3>
          <p className="text-sm text-slate-400 mt-1">
            Add Criminal Appeal AI to your home screen for quick access
          </p>
        </div>
      </div>
      <div className="flex gap-2 mt-4">
        <Button 
          variant="ghost" 
          size="sm" 
          className="flex-1 text-slate-400 hover:text-white hover:bg-slate-800"
          onClick={handleDismiss}
        >
          Not now
        </Button>
        <Button 
          size="sm" 
          className="flex-1 bg-amber-500 hover:bg-amber-600 text-slate-900"
          onClick={handleInstall}
        >
          Install
        </Button>
      </div>
    </div>
  );
};

export default InstallPrompt;
