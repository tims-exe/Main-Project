import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
    const token = request.cookies.get('access_token')?.value;
    const isLoginPage = request.nextUrl.pathname === '/login';
    const isHome = request.nextUrl.pathname.startsWith('/home');

    // Redirect to login if accessing protected route without token
    if (isHome && !token) {
        return NextResponse.redirect(new URL('/login', request.url));
    }

    // Redirect to home if accessing login with valid token
    if (isLoginPage && token) {
        return NextResponse.redirect(new URL('/home', request.url));
    }

    return NextResponse.next();
}

export const config = {
    matcher: ['/home/:path*', '/login'],
};