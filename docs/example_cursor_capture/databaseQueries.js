/**
 * Database Query Methods for Cursor Extension
 *
 * Extracted and de-minified from example_cursor_capture/extension.js
 *
 * These methods read trace and log data from Cursor's SQLite database.
 * Cursor stores data in ItemTable as key-value pairs, not traditional SQL tables.
 */

const sqlite3 = require("@vscode/sqlite3").verbose();
const vscode = require("vscode");

// Simple logger implementation (replace with actual logger if available)
const logger = {
  debug: (msg, meta) => console.log(`[DEBUG] ${msg}`, meta || ""),
  info: (msg, meta) => console.log(`[INFO] ${msg}`, meta || ""),
  warn: (msg, meta, err) =>
    console.warn(`[WARN] ${msg}`, meta || "", err || ""),
  error: (msg, meta, err) =>
    console.error(`[ERROR] ${msg}`, meta || "", err || ""),
};

/**
 * Database loader class for reading from Cursor's workspace database
 */
class DatabaseLoader {
  /**
   * Load data from ItemTable with optional key filtering
   *
   * @param {string} dbPath - Path to state.vscdb file
   * @param {string} tableName - Table name (default: "ItemTable")
   * @param {string|string[]} keyFilter - Single key or array of keys to filter
   * @returns {Promise<Map<string, any>>} Map of key-value pairs
   */
  static loadDatabaseTable(dbPath, tableName = "ItemTable", keyFilter = null) {
    let query = `SELECT * FROM ${tableName} WHERE value IS NOT NULL`;
    const params = [];

    if (typeof keyFilter === "string") {
      query += " AND key = ?";
      params.push(keyFilter);
    } else if (Array.isArray(keyFilter) && keyFilter.length > 0) {
      query += ` AND key IN (${keyFilter.map(() => "?").join(",")})`;
      params.push(...keyFilter);
    }

    return this.loadFromDatabase(dbPath, query, params);
  }

  /**
   * Load conversation data from cursorDiskKV table with LIKE pattern matching
   *
   * @param {string} dbPath - Path to state.vscdb file
   * @param {string[]} keyPatterns - Array of LIKE patterns for key matching
   * @returns {Promise<Map<string, any>>} Map of key-value pairs
   */
  static loadCursorConversationData(dbPath, keyPatterns = []) {
    let query = "SELECT * FROM cursorDiskKV WHERE value IS NOT NULL";

    if (keyPatterns.length > 0) {
      query += " AND (";
      for (let i = 0; i < keyPatterns.length; i++) {
        if (i === 0) {
          query += ` key LIKE '%${keyPatterns[i]}%' `;
        } else {
          query += ` OR key LIKE '%${keyPatterns[i]}%' `;
        }
      }
      query += ")";
    }

    return this.loadFromDatabase(dbPath, query, []);
  }

  /**
   * Core database loading method with WAL mode handling
   *
   * @param {string} dbPath - Path to state.vscdb file
   * @param {string} query - SQL query string
   * @param {any[]} params - Query parameters
   * @returns {Promise<Map<string, any>>} Map of key-value pairs
   */
  static loadFromDatabase(dbPath, query, params) {
    return new Promise((resolve, reject) => {
      const resultMap = new Map();

      logger.debug(`Opening database in read-only mode: ${dbPath}`);

      // Open database in read-only mode first
      const db = new sqlite3.Database(dbPath, sqlite3.OPEN_READONLY, (err) => {
        if (err) {
          logger.error("Failed to open database", { path: dbPath }, err);
          reject(err);
          return;
        }

        // Check current journal mode
        db.get("PRAGMA journal_mode;", [], (err, row) => {
          if (err) {
            logger.error("Failed to check journal mode", {}, err);
            db.close();
            reject(err);
            return;
          }

          const journalMode = row?.journal_mode?.toUpperCase();
          logger.debug(`Current journal mode: ${journalMode}`, {
            path: dbPath,
          });

          // If already in WAL mode, proceed with query
          if (journalMode === "WAL") {
            return executeQuery(db);
          }

          // Otherwise, set to WAL mode
          logger.debug("Setting database to WAL mode", { path: dbPath });
          db.close((closeErr) => {
            if (closeErr) {
              logger.error("Failed to close database", {}, closeErr);
              reject(closeErr);
              return;
            }

            // Reopen in read-write mode to set WAL
            const rwDb = new sqlite3.Database(
              dbPath,
              sqlite3.OPEN_READWRITE,
              (rwErr) => {
                if (rwErr) {
                  logger.error(
                    "Failed to open database in read/write mode",
                    {},
                    rwErr
                  );
                  reject(rwErr);
                  return;
                }

                rwDb.exec("PRAGMA journal_mode=WAL;", (execErr) => {
                  if (execErr) {
                    logger.error("Failed to set WAL mode", {}, execErr);
                    rwDb.close();
                    reject(execErr);
                    return;
                  }

                  logger.debug("Successfully set database to WAL mode", {
                    path: dbPath,
                  });
                  rwDb.close((closeErr2) => {
                    if (closeErr2) {
                      logger.error(
                        "Failed to close r/w database",
                        {},
                        closeErr2
                      );
                      reject(closeErr2);
                      return;
                    }

                    // Reopen in read-only mode after WAL mode change
                    logger.debug(
                      "Reopening database in read-only mode after WAL mode change"
                    );
                    const roDb = new sqlite3.Database(
                      dbPath,
                      sqlite3.OPEN_READONLY,
                      (roErr) => {
                        if (roErr) {
                          logger.error(
                            "Failed to reopen database in read-only mode",
                            {},
                            roErr
                          );
                          reject(roErr);
                          return;
                        }
                        return executeQuery(roDb);
                      }
                    );
                  });
                });
              }
            );
          });
        });
      });

      /**
       * Execute the actual query and parse results
       */
      function executeQuery(database) {
        database.all(query, params, (err, rows) => {
          if (err) {
            logger.error("Error executing query", { query }, err);
            database.close();
            reject(err);
            return;
          }

          // Parse each row - values are stored as BLOB/text JSON
          rows.forEach((row) => {
            try {
              const key = row.key.toString();
              const value = row.value;

              // Try to parse as JSON, fallback to string
              try {
                const parsedValue = JSON.parse(value.toString());
                resultMap.set(key, parsedValue);
              } catch {
                // If not JSON, store as string
                resultMap.set(key, value.toString());
              }
            } catch (parseErr) {
              logger.warn("Failed to parse row", { key: row.key }, parseErr);
            }
          });

          database.close((closeErr) => {
            if (closeErr) {
              logger.error("Error closing database", {}, closeErr);
              reject(closeErr);
              return;
            }

            logger.debug("Successfully completed database operation", {
              path: dbPath,
            });
            resolve(resultMap);
          });
        });
      }
    });
  }
}

/**
 * Workspace loader for finding and loading current workspace data
 */
class WorkspaceLoader {
  constructor(pathsService, context) {
    this.pathsService = pathsService;
    this.context = context;
    this.logger = logger;
  }

  /**
   * Set a value in workspace state
   */
  set(key, value) {
    this.context.workspaceState.update(key, value);
    this.logger.debug(`Stored workspace value for key: ${key}`, { value });
  }

  /**
   * Get a value from workspace state
   */
  get(key) {
    return this.context.workspaceState.get(key);
  }

  /**
   * Load current workspace database and data
   *
   * @returns {Promise<Object|undefined>} Workspace data object or undefined
   */
  async loadCurrentWorkspace() {
    const workspaceStoragePath = this.pathsService.getWorkspaceStoragePath();
    const workspaceStorageFolder =
      this.pathsService.getWorkspaceStorageFolder();

    this.logger.info("Workspace storage path", {
      path: workspaceStoragePath,
      folder: workspaceStorageFolder,
    });

    const workspaceFile = vscode.workspace.workspaceFile;
    const workspaceFolders = vscode.workspace.workspaceFolders;

    this.logger.info("Loading current workspace", {
      file: workspaceFile?.fsPath,
      hasWorkspaceFolders: !!workspaceFolders,
      folderCount: workspaceFolders?.length ?? 0,
      workspaceFolders: workspaceFolders?.map((f) => f.uri.toString()),
    });

    if (
      !workspaceFile &&
      (!workspaceFolders ||
        workspaceFolders.length === 0 ||
        !workspaceFolders[0])
    ) {
      this.logger.debug("No workspace file and no workspace folders found");
      return;
    }

    const fs = require("fs").promises;
    const path = require("path");

    // Read all directories in workspace storage
    const entries = await fs.readdir(workspaceStoragePath, {
      withFileTypes: true,
    });
    const directories = entries.filter((e) => e.isDirectory());

    const matchingWorkspaces = [];

    for (const dir of directories) {
      const workspaceJsonPath = path.join(
        workspaceStoragePath,
        dir.name,
        "workspace.json"
      );
      const stateDbPath = path.join(
        workspaceStoragePath,
        dir.name,
        "state.vscdb"
      );

      if (
        !(await fs
          .access(workspaceJsonPath)
          .then(() => true)
          .catch(() => false)) ||
        !(await fs
          .access(stateDbPath)
          .then(() => true)
          .catch(() => false))
      ) {
        this.logger.debug(
          "Skipping directory, no workspace.json or no state.vscdb found",
          {
            directory: dir.name,
          }
        );
        continue;
      }

      try {
        const workspaceJsonContent = await fs.readFile(
          workspaceJsonPath,
          "utf8"
        );
        const workspaceData = JSON.parse(workspaceJsonContent);
        const workspacePath = workspaceData.workspace || workspaceData.folder;

        if (!workspacePath) {
          this.logger.debug(
            "Skipping directory, no workspace or folderpath found in workspace.json",
            {
              directory: dir.name,
              workspaceJsonPath,
            }
          );
          continue;
        }

        // Check if this matches current workspace
        const matches = workspaceFile
          ? workspaceFile.toString() === workspacePath
          : workspaceFolders?.[0]?.uri.toString() === workspacePath;

        if (matches) {
          // Load ItemTable data from database
          const itemTableData = await DatabaseLoader.loadDatabaseTable(
            stateDbPath
          );
          const dataObject = Object.fromEntries(itemTableData?.entries() ?? []);

          const stats = await fs.stat(stateDbPath);
          const mtimeMs = stats.mtimeMs;

          this.logger.info("Found matching workspace directory", {
            matchingDirectory: dir.name,
            workspacePath,
            workspaceFolder: workspaceStorageFolder,
            workspaceData,
            entryCount: Object.keys(dataObject).length,
            timestamp: mtimeMs,
          });

          matchingWorkspaces.push({
            id: dir.name,
            path: workspacePath,
            folder: workspaceStorageFolder,
            dbPath: stateDbPath,
            timestamp: mtimeMs,
            data: dataObject,
          });
        }
      } catch (err) {
        this.logger.warn(
          "Failed to process workspace directory",
          {
            directory: dir.name,
            workspaceJsonPath,
          },
          err instanceof Error ? err : new Error(String(err))
        );
        continue;
      }
    }

    this.logger.debug("Matching workspaces", {
      count: matchingWorkspaces.length,
      ids: matchingWorkspaces.map((w) => w.id),
      paths: matchingWorkspaces.map((w) => w.path),
      dbPaths: matchingWorkspaces.map((w) => w.dbPath),
      timestamps: matchingWorkspaces.map((w) => w.timestamp),
    });

    if (matchingWorkspaces.length === 0) {
      this.logger.error("No matching workspace found", {
        file: workspaceFile?.fsPath,
        hasWorkspaceFolders: !!workspaceFolders,
        folderCount: workspaceFolders?.length ?? 0,
        workspaceFolders: workspaceFolders?.map((f) => f.uri.toString()),
      });
      return undefined;
    }

    // Select the most recently modified workspace
    const selectedWorkspace = matchingWorkspaces.reduce((latest, current) => {
      return (current.timestamp ?? 0) > (latest.timestamp ?? 0)
        ? current
        : latest;
    });

    this.logger.info("Selected matching workspace", {
      directory: selectedWorkspace.id,
      timestamp: selectedWorkspace.timestamp,
      path: selectedWorkspace.path,
      dbPath: selectedWorkspace.dbPath,
      entryCount: Object.keys(selectedWorkspace.data).length,
    });

    return selectedWorkspace;
  }
}

module.exports = {
  DatabaseLoader,
  WorkspaceLoader,
};
