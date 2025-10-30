export interface GoogleCredentialResponse {
    credential: string;
    select_by: string;
}

export interface User {
    id: string;
    email: string;
    first_name: string | null;
    last_name: string | null;
    profile_picture: string | null;
}

export interface AuthResponse {
    access_token: string;
    token_type: string;
    user: User;
}

export interface GoogleAccounts {
    id: {
        initialize: (config: GoogleIdConfiguration) => void;
        renderButton: (parent: HTMLElement, options: GoogleButtonConfiguration) => void;
        prompt: (momentListener?: (notification: unknown) => void) => void;
    };
}

export interface GoogleIdConfiguration {
    client_id: string;
    callback: (response: GoogleCredentialResponse) => void;
    auto_select?: boolean;
    cancel_on_tap_outside?: boolean;
}

export interface GoogleButtonConfiguration {
    theme?: 'outline' | 'filled_blue' | 'filled_black';
    size?: 'large' | 'medium' | 'small';
    text?: 'signin_with' | 'signup_with' | 'continue_with' | 'signin';
    shape?: 'rectangular' | 'pill' | 'circle' | 'square';
    logo_alignment?: 'left' | 'center';
    width?: number;
    locale?: string;
}

declare global {
    interface Window {
        google?: {
            accounts: GoogleAccounts;
        };
    }
}