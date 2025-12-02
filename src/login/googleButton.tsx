import React, { useEffect, useRef } from "react";

declare global {
    interface Window {
        google?: any;
    }
}

interface LoginButtonProps {
    onSuccess: (response: any) => void;
    onError?: () => void;
}


function LoginButton({ onSuccess }: LoginButtonProps){
    const buttonRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        const interval = setInterval(() => {
            if((window as any).googleScriptLoaded && window.google) {
                window.google.accounts.id.initialize({
                    client_id: process.env.REACT_APP_GOOGLE_ID,
                    callback: onSuccess
                });
                window.google.accounts.id.renderButton(buttonRef.current, {
                    theme: "outline",
                    size: "large"
                });
            };

            clearInterval(interval);
        }, 100);
        return () => clearInterval(interval);
    }, [onSuccess]);

    return <div ref={buttonRef}></div>
}

export default LoginButton;