import type { User } from "../../api/types";
import { APP_VERSION } from "../../version";

interface UserMenuProps {
  user: User;
  onLogout: () => void;
}

export function UserMenu({ user, onLogout }: UserMenuProps) {
  return (
    <div className="user-menu">
      {user.github_avatar_url && (
        <img src={user.github_avatar_url} alt="" className="user-avatar" />
      )}
      <div>
        <div className="user-name">{user.github_name || user.github_login}</div>
        <div className="version-notice">{APP_VERSION}</div>
        <button className="btn btn-ghost btn-sm" onClick={onLogout}>
          Sign out
        </button>
      </div>
    </div>
  );
}
