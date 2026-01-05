# Customer Form UI Design

**Module:** Customer
**Feature:** Create Customer Form
**Designer:** shadcn-ui-agent
**Date:** 2026-01-01

---

## Overview

This document provides detailed UI design specifications for the Customer creation form. The form allows bank staff to create new customer accounts with credit assessment validation.

---

## Requirements

### Functional Requirements
- **FR-001**: Customer Creation with Credit Assessment
- Must capture: name, email, phone, address, credit score
- Validate credit score >= 700 (business rule BR-CUST-001)
- Handle duplicate email errors (CUST-002)
- Handle credit assessment failures (CUST-004)

### User Interactions Needed
1. Navigate to form
2. Fill in customer details
3. Submit form
4. View validation errors (client-side and server-side)
5. Redirect to customer detail page on success

### Validation Rules
- **Name**: Required, min 2 characters
- **Email**: Required, valid email format, unique
- **Phone**: Required, valid phone format (E.164)
- **Address**: Required, min 10 characters
- **Credit Score**: Required, integer, 0-850 range

### Error Handling Needs
- Client-side validation (zod)
- Server-side error display (API errors)
- Loading state during submission
- Network error handling

---

## Component Selection

### Main Components

1. **Form** (`@/components/ui/form`)
   - **Variant:** default
   - **Props:** `onSubmit`, validation schema (zod)
   - **Reason:** Integrates seamlessly with react-hook-form for comprehensive validation and error handling

2. **Card** (`@/components/ui/card`)
   - **Variant:** default
   - **Props:** None (container)
   - **Reason:** Provides visual container and elevation for the form, consistent with banking UI patterns

3. **Input** (`@/components/ui/input`)
   - **Variant:** default
   - **Props:** `type` (text, email, tel, number), `placeholder`, `required`, `disabled`
   - **Reason:** Standard text input with built-in validation support and accessibility features

4. **Button** (`@/components/ui/button`)
   - **Variants:**
     - default (submit button)
     - outline (cancel button)
   - **Props:** `type="submit"`, `disabled`, `loading`
   - **Reason:** Clear call-to-action with loading state support for async operations

5. **Alert** (`@/components/ui/alert`)
   - **Variant:** destructive (for errors)
   - **Props:** `variant`, `title`, `description`
   - **Reason:** Prominent display of API errors (duplicate email, credit assessment failure)

6. **Label** (`@/components/ui/label`)
   - **Variant:** default
   - **Props:** `htmlFor` (accessibility)
   - **Reason:** Ensures proper form accessibility with screen readers

---

### Supporting Components

- **FormField**: Wrapper for each form field (from shadcn form)
- **FormItem**: Container for label + input + error
- **FormLabel**: Accessible label
- **FormControl**: Input wrapper
- **FormMessage**: Error message display
- **CardHeader**: Form title section
- **CardTitle**: "Create New Customer" heading
- **CardContent**: Form body
- **CardFooter**: Submit/cancel buttons

---

## Component Structure

```
CustomerForm
├── Card
│   ├── CardHeader
│   │   └── CardTitle: "Create New Customer"
│   │       └── CardDescription: "Enter customer details and credit information"
│   └── CardContent
│       ├── Alert (conditional - only shown on API errors)
│       │   ├── AlertTitle: "Error"
│       │   └── AlertDescription: {error message}
│       │
│       └── Form (react-hook-form)
│           ├── FormField: name
│           │   ├── FormLabel: "Full Name"
│           │   ├── FormControl
│           │   │   └── Input (type="text", placeholder="John Doe")
│           │   └── FormMessage (validation error)
│           │
│           ├── FormField: email
│           │   ├── FormLabel: "Email Address"
│           │   ├── FormControl
│           │   │   └── Input (type="email", placeholder="john.doe@example.com")
│           │   └── FormMessage
│           │
│           ├── FormField: phone
│           │   ├── FormLabel: "Phone Number"
│           │   ├── FormControl
│           │   │   └── Input (type="tel", placeholder="+1 (555) 123-4567")
│           │   └── FormMessage
│           │
│           ├── FormField: address
│           │   ├── FormLabel: "Address"
│           │   ├── FormControl
│           │   │   └── Textarea (placeholder="123 Main St, City, State, ZIP")
│           │   └── FormMessage
│           │
│           ├── FormField: credit_score
│           │   ├── FormLabel: "Credit Score"
│           │   ├── FormControl
│           │   │   └── Input (type="number", min=0, max=850, placeholder="750")
│           │   └── FormMessage
│           │   └── FormDescription: "Score must be 700 or higher"
│           │
│           └── CardFooter
│               ├── Button (type="submit", variant="default", disabled={isSubmitting})
│               │   └── {isSubmitting ? "Creating..." : "Create Customer"}
│               └── Button (type="button", variant="outline", onClick={onCancel})
│                   └── "Cancel"
```

---

## State Management

```typescript
interface FormState {
  // Form data managed by react-hook-form
  formData: CustomerCreate;

  // Submission state
  isSubmitting: boolean;

  // API error (if any)
  apiError: {
    code: string;    // "CUST-002", "CUST-004", etc.
    message: string; // User-friendly message
  } | null;
}
```

### State Flow

1. **Initial State**: Empty form, not submitting, no errors
2. **User Input**: react-hook-form manages field state
3. **Validation**: Real-time validation on blur
4. **Submit**: `isSubmitting = true`, disable form
5. **Success**: Redirect to `/customers/{id}`
6. **Error**: `isSubmitting = false`, show `apiError` in Alert

---

## Validation Schema

```typescript
import { z } from "zod";

const customerFormSchema = z.object({
  name: z.string()
    .min(2, "Name must be at least 2 characters")
    .max(255, "Name is too long"),

  email: z.string()
    .email("Invalid email format")
    .max(255, "Email is too long"),

  phone: z.string()
    .regex(
      /^\+?[1-9]\d{1,14}$/,
      "Invalid phone number format (use E.164 format: +1234567890)"
    ),

  address: z.string()
    .min(10, "Address must be at least 10 characters")
    .max(500, "Address is too long"),

  credit_score: z.coerce
    .number({
      required_error: "Credit score is required",
      invalid_type_error: "Credit score must be a number"
    })
    .int("Credit score must be an integer")
    .min(0, "Credit score cannot be negative")
    .max(850, "Credit score cannot exceed 850")
    .refine(
      (score) => score >= 700,
      "Credit score must be 700 or higher for account approval"
    )
});

type CustomerFormValues = z.infer<typeof customerFormSchema>;
```

---

## User Interactions

### 1. Load Form
**Action:** User navigates to `/customers/new`

**UI State:**
- Show empty form with labels
- All fields enabled
- Submit button enabled with text "Create Customer"
- No errors shown

---

### 2. Fill Form
**Action:** User enters data in fields

**UI Behavior:**
- **On Focus**: Field border changes color (focus ring)
- **On Blur**: Client-side validation runs
  - If invalid: Show red border + error message below field
  - If valid: Show green checkmark (optional)
- **Submit Button**:
  - Disabled if form has validation errors
  - Enabled if all fields valid

---

### 3. Submit Form (Success Path)
**Action:** User clicks "Create Customer"

**UI Flow:**
1. Button text changes to "Creating..."
2. Loading spinner appears on button
3. All form fields disabled
4. API call: `POST /customers`
5. **On Success:**
   - Show toast notification: "Customer created successfully"
   - Redirect to `/customers/{id}`
   - Customer detail page displays

---

### 4. Submit Form (Validation Error)
**Action:** User clicks submit with invalid data

**UI Flow:**
1. react-hook-form prevents submission
2. Focus moves to first invalid field
3. All validation errors shown simultaneously
4. No API call made

---

### 5. Submit Form (API Error)
**Action:** API returns error (409, 400, 500)

**UI Flow:**
1. Button returns to normal state ("Create Customer")
2. All form fields re-enabled
3. Alert component appears at top of form:
   - **For CUST-002 (409)**:
     - Title: "Email Already Exists"
     - Description: "A customer with this email address already exists. Please use a different email."
   - **For CUST-004 (400)**:
     - Title: "Credit Assessment Failed"
     - Description: "Credit score is below the minimum threshold (700). Account creation denied."
   - **For Network Error**:
     - Title: "Network Error"
     - Description: "Unable to connect to server. Please check your internet connection and try again."
4. User data remains in form (not cleared)
5. User can correct and resubmit

---

### 6. Cancel
**Action:** User clicks "Cancel" button

**UI Flow:**
1. Show confirmation dialog: "Discard changes?"
2. If confirmed: Navigate back to `/customers` (list page)
3. If cancelled: Stay on form

---

## Error Handling

### Error Mapping Table

| Error Code | HTTP Status | Alert Variant | Display Message |
|------------|-------------|---------------|-----------------|
| CUST-001   | 404         | destructive   | "Customer not found" (shouldn't occur on create) |
| CUST-002   | 409         | destructive   | "Email already exists. Please use a different email address." |
| CUST-003   | 400         | destructive   | "Invalid credit score provided." |
| CUST-004   | 400         | destructive   | "Credit assessment failed. Score must be 700 or higher." |
| Network Error | -        | destructive   | "Network error. Please check your connection and try again." |
| 500        | 500         | destructive   | "Server error. Please try again later or contact support." |

### Error Display Strategy

**Client-Side Errors (Validation):**
- Display inline below each field
- Red border on input
- Show immediately on blur
- Clear when user corrects input

**Server-Side Errors (API):**
- Display in Alert at top of form
- Dismissible (X button)
- Persist until dismissed or form resubmitted
- Include error code in dev mode (for debugging)

---

## Accessibility

### ARIA Attributes
- All inputs have `aria-label` or associated `<label>`
- Error messages have `aria-live="polite"` for screen reader announcements
- Form has `aria-labelledby` pointing to CardTitle
- Submit button has `aria-disabled` when disabled

### Keyboard Navigation
- **Tab**: Move between fields
- **Shift+Tab**: Move backwards
- **Enter**: Submit form (when on submit button)
- **Escape**: Cancel/close (optional)

### Focus Management
- On validation error: Focus first invalid field
- On API error: Focus Alert (for screen reader)
- On success: Focus announcement region

### Screen Reader Announcements
- "Creating customer..." when submitting
- "Customer created successfully" on success
- Error messages announced when shown
- Field descriptions read on focus

### Color Contrast
- All text meets WCAG AA standards (4.5:1 ratio)
- Error messages use both color AND icon (not color alone)
- Focus indicators visible and high contrast

---

## Responsive Design

### Mobile (< 640px)
```css
Layout:
- Single column
- Full-width inputs
- Stacked buttons (vertical)
- Larger touch targets (min 44px)
- Padding: 16px

Form:
- CardTitle: text-xl
- Inputs: text-base, h-12
- Buttons: w-full, h-12
```

### Tablet (640px - 1024px)
```css
Layout:
- Single column with more padding
- Max width: 600px, centered
- Side padding: 32px
- Buttons: side-by-side

Form:
- CardTitle: text-2xl
- Inputs: text-base, h-11
- Buttons: auto width, h-11
```

### Desktop (> 1024px)
```css
Layout:
- Max width: 700px, centered
- Two-column for name/email (optional)
- Buttons: side-by-side, right-aligned

Form:
- CardTitle: text-3xl
- Inputs: text-base, h-10
- Buttons: auto width, h-10
- More generous spacing
```

---

## Installation Commands

```bash
# Navigate to frontend directory
cd output/legacy-banking/frontend

# Install shadcn/ui components
npx shadcn-ui@latest add form
npx shadcn-ui@latest add input
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add alert
npx shadcn-ui@latest add label
npx shadcn-ui@latest add textarea

# Install form dependencies
npm install react-hook-form zod @hookform/resolvers
```

---

## Additional Dependencies

```bash
# If not already installed
npm install @radix-ui/react-label
npm install @radix-ui/react-slot
npm install class-variance-authority
npm install clsx
npm install tailwind-merge
```

---

## Implementation Notes for Infrastructure Agent

### Step-by-Step Implementation

1. **Install Components** (run commands above)

2. **Create API Client** (`frontend/src/api/customer.ts`)
   - Import types from `contracts/Customer/types.ts`
   - Implement `createCustomer()` function
   - Handle all error codes

3. **Create Form Component** (`frontend/src/components/Customer/CustomerForm.tsx`)
   - Follow component structure exactly as diagrammed
   - Use react-hook-form with zodResolver
   - Implement state management as specified
   - Add all accessibility features

4. **Create Page** (`frontend/src/app/customers/new/page.tsx`)
   - Import CustomerForm
   - Add metadata
   - Render form

5. **Test**
   - Verify all validations work
   - Test all error scenarios
   - Check responsive behavior
   - Test keyboard navigation
   - Verify screen reader support

### Validation Checklist

- [ ] Form validates on blur
- [ ] Submit disabled when invalid
- [ ] API errors displayed in Alert
- [ ] Success redirects to detail page
- [ ] Cancel prompts for confirmation
- [ ] Keyboard navigation works
- [ ] Screen reader announces errors
- [ ] Responsive on all screen sizes
- [ ] All error codes handled
- [ ] Loading state shown during submit

---

## Design Decisions

### Why Card?
- Provides visual hierarchy and separation
- Common pattern in banking/financial UIs
- Works well for standalone forms

### Why Alert for API Errors?
- More prominent than inline messages
- Can include detailed information
- Dismissible by user
- Semantically correct for errors

### Why react-hook-form?
- Best-in-class form library for React
- Excellent performance (uncontrolled inputs)
- Built-in validation support
- Works seamlessly with shadcn Form component

### Why zod?
- Type-safe validation
- Reusable schemas
- Great TypeScript integration
- Can share schemas between client/server

---

## Future Enhancements

These are NOT part of the current implementation but could be added later:

1. **Autosave Draft**: Save form data to localStorage
2. **Address Autocomplete**: Google Places API integration
3. **Credit Score Info**: Tooltip explaining score ranges
4. **Multiple Addresses**: Support billing vs. mailing address
5. **File Upload**: Attach documents (ID, proof of address)
6. **Real-time Email Check**: Validate email uniqueness as user types (debounced)

---

**End of Design Document**

---

**Next Steps for infrastructure-agent:**
1. Read this document carefully
2. Install all components
3. Implement CustomerForm.tsx following structure
4. Create page.tsx
5. Test thoroughly
6. Run validation commands
