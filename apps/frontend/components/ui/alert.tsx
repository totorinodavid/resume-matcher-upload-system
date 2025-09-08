import * as React from 'react'
import { cn } from '../utils'

const variantClasses: Record<string,string> = {
  default: 'bg-gray-50 border-gray-200 text-gray-800',
  destructive: 'bg-red-50 border-red-300 text-red-800'
}

export interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'destructive'
}

export function Alert({ className, variant = 'default', ...props }: AlertProps) {
  return (
    <div
      role="alert"
      className={cn(
        'relative w-full rounded-lg border px-4 py-3 text-sm flex items-start gap-2',
        variantClasses[variant] || variantClasses.default,
        className
      )}
      {...props}
    />
  )
}

export function AlertDescription({ className, ...props }: React.HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p
      className={cn('text-sm leading-relaxed', className)}
      {...props}
    />
  )
}
