# Frequently Asked Questions

### React Native Error: ENOSPC: System limit for number of file watchers reached

The meaning of this error is that the number of files monitored by the system has reached the limit.

Linux uses the inotify package to observe filesystem events, individual files or directories.

Since React / Angular hot-reloads and recompiles files on save it needs to keep track of all project's files. Increasing the inotify watch limit should hide the warning messages.

**Solution:**

1. Modify the number of system monitoring files

For example, in Ubuntu:

```sh
sudo vim /etc/sysctl.conf
```

Add a line at the bottom. Then save and exit!

```
fs.inotify.max_user_watches=524288
```

To check whether you have correctly set it,

```sh
sudo sysctl -p
```

If you see `fs.inotify.max_user_watches = 524288` in the command line, then it is solved!