import React from 'react';

// Em React 19+, precisamos estender o módulo 'react' diretamente,
// pois o namespace JSX não é mais puramente global.
declare module 'react' {
  namespace JSX {
    interface IntrinsicElements {
      'model-viewer': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement> & {
        src?: string;
        'ios-src'?: string;
        alt?: string;
        ar?: boolean;
        'auto-rotate'?: boolean;
        'camera-controls'?: boolean;
        'shadow-intensity'?: string;
        'camera-orbit'?: string;
        'field-of-view'?: string;
        poster?: string;
        loading?: 'auto' | 'lazy' | 'eager';
        reveal?: 'auto' | 'manual';
        // Importante: 'ref' precisa ser tipado explicitamente para Web Components no React
        ref?: React.MutableRefObject<any>; 
        [key: string]: any; 
      }, HTMLElement>;
    }
  }
}