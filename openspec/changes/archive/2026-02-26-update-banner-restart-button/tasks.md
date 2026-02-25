## 1. UpdateBanner Widget

- [x] 1.1 Change `UpdateBanner` base class from `Static` to `Horizontal` and add `compose()` method yielding a `Static` (id=`update-banner-text`) and a `Button` (id=`btn-update-restart`, variant=`warning`, label="Restart to Update")
- [x] 1.2 Update `DEFAULT_CSS` for `UpdateBanner` to style the horizontal layout: `Static` gets `width: 1fr`, `Button` gets `min-width: 20; margin-left: 1`
- [x] 1.3 Update `show_update()` to set text on the child `Static` widget instead of `self.update()`, and remove the " — restart to update" text suffix

## 2. Button Handler

- [x] 2.1 Add `@on(Button.Pressed, "#btn-update-restart")` handler on `Dashboard` that runs `git pull --ff-only` in the StackTUI repo then calls `os.execv()` to re-exec

## 3. Verification

- [x] 3.1 Run the app and confirm the banner renders correctly with button alongside text when updates are available
- [x] 3.2 Confirm clicking the button restarts the app
- [x] 3.3 Confirm the banner hides when no updates are available
