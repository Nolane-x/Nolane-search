# Telegram Workspace UX research and implementation

Date: 2026-11-25

## UX problem found in the current bot

The previous `/start` dashboard tried to place nine rows of unrelated destinations and eight search/AI modes directly into one inline keyboard. Tool Center then continued the same text-heavy pattern by presenting category descriptions, tool details, job traces and pagination as successive chat messages.

Telegram chat messages cannot be styled like a native application. Inline keyboards are useful for short contextual actions, but they are a poor place to reproduce a multi-screen workspace with search filters, a large tool catalog, a chat composer, job lists and personal-index management. The result was a long, visually repetitive menu and a chat history used as an accidental navigation stack.

## Research findings

Telegram's official Mini Apps documentation explicitly positions the inline `web_app` button as the appropriate launch mechanism for a full-fledged web service or integration. It also recommends mobile-first responsive layouts, live theme adaptation, safe-area support, accessible labels and lightweight animations. The Telegram WebApp SDK exposes theme parameters, the native BackButton and haptic feedback.

- Official Telegram Mini Apps documentation: https://core.telegram.org/bots/webapps
- Official guidance for Mini App theme and safe-area design: https://core.telegram.org/bots/webapps#designing-mini-apps
- Inline Mini App launch guidance: https://core.telegram.org/bots/webapps#inline-button-mini-apps
- Menu button launch guidance: https://core.telegram.org/bots/webapps#launching-mini-apps-from-the-menu-button

Public GitHub examples reinforce a recurring architecture: a small application shell, separate screens, Telegram theme variables, BackButton handling, haptics and same-origin API integration. The repositories below were reviewed as implementation references, not copied into this project:

- Imolatte/telegram-miniapp: https://github.com/Imolatte/telegram-miniapp
- zenhtml/telegram-mini-app: https://github.com/zenhtml/telegram-mini-app
- telegram-mini-apps organization and SDK templates: https://github.com/telegram-mini-apps
- usernein/react-mini-app: https://github.com/usernein/react-mini-app

Many examples use React, TypeScript and Vite. That is a good fit for independently built Mini Apps, but this repository already serves the private workspace directly from a Cloudflare Worker and has a functioning inline HTML/TypeScript page pattern. Adding a new framework, separate asset build, package tree and deployment surface would increase operational complexity for a UI whose backend APIs already exist. This implementation therefore keeps a self-contained same-origin page, while adopting the interaction patterns rather than importing framework code.

## New information architecture

The chat itself now stays small:

1. One primary `✦ Mở Nolane Workspace` inline Web App button.
2. A few quick native search/AI modes for users who want to stay in the chat.
3. Tool Center and status as compact shortcuts.

The Mini App provides five dedicated bottom-navigation areas:

- **Tổng quan** — command-center hero, quick actions, health/tool/job counters and recent searches.
- **Tìm kiếm** — Search Studio with mode selection, result cards and optional evidence synthesis.
- **AI** — conversational interface and the current browser-to-Telegram file-processing flow.
- **Tools** — catalog search, category filter, tool information and recent job status.
- **Kho riêng** — Personal Index, website crawl form and crawl history.

Media discovery remains a separate same-origin Media Studio linked from the overview rather than another large card in the chat keyboard.

## Visual and interaction system

- A dark, layered workspace palette with a single accent color, restrained gradients and clear spacing hierarchy.
- Telegram theme variables are used as the source of truth for background, surface, text, hint, link and button colors. The theme-change event updates header and background colors.
- Mobile-first card grids collapse from three columns to two or one as the available width changes.
- Bottom navigation separates product areas; search results, tool cards and job records each have distinct visual hierarchy.
- Telegram's native BackButton follows in-app navigation; light haptics are used on tab and successful/error actions.
- Safe-area and content-safe-area insets are respected around the page and fixed bottom navigation.
- Reduced-motion preferences disable the small view transitions.
- All untrusted API results are inserted as text nodes and source URLs are accepted only when HTTPS.

## Authentication and trust boundary

The Mini App does not trust client-provided Telegram user IDs or use Telegram `initDataUnsafe` as authorization. The bot creates a cryptographically random, single-use ticket only for an allowlisted user in a private chat. D1 stores only the SHA-256 ticket hash, the ticket is bound to the Telegram user/chat and expires after five minutes. The existing `POST /api/auth/exchange` consumes it once and issues the existing Secure, HttpOnly, SameSite=Strict seven-day session cookie. The ticket is removed from browser history immediately after successful exchange.

All subsequent data operations use existing same-origin Worker APIs and existing session authorization. No new account table, OAuth service, token in localStorage, API provider or cross-origin backend is added.

The Mini App route itself returns HTML but exposes no private data until an authenticated API session exists. Writes still pass through the same-origin request guard and owner-session checks.

## Known operational boundary

The inline `web_app` button is sent only after the bot has verified that the chat is private and the Telegram user is allowlisted. It should be tested in that private chat; it is not a group-chat interface. After `/start`, the bot also attempts to configure a per-chat Menu button through Bot API `setChatMenuButton`. That persistent launcher uses the static same-origin `/telegram` URL and depends on the current session cookie; the inline button remains the one-time bootstrap path. If the per-chat Menu-button API call fails, the chat keyboard continues to work and the failure is logged.

No production deployment or BotFather configuration is performed by this branch. The Worker configures the per-chat Menu shortcut itself after `/start`; BotFather setup is optional and not required for this private-chat flow. Live verification still requires opening both the Workspace inline button and Telegram Menu shortcut in the actual Telegram app on Android/iOS/Desktop and checking the viewport, theme switching, navigation, and authentication in that client.
