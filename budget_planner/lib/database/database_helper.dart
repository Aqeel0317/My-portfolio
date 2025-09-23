import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

class DatabaseHelper {
  static final _databaseName = "expenseTracker.db";
  static final _databaseVersion = 1;

  static final transactionsTable = 'transactions';
  static final budgetsTable = 'budgets';
  
  // Singleton instance
  static Database? _database;
  static final DatabaseHelper instance = DatabaseHelper._init();
  DatabaseHelper._init();
  

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  _initDatabase() async {
    final path = join(await getDatabasesPath(), _databaseName);
    return await openDatabase(
      path,
      version: _databaseVersion,
      onCreate: _onCreate,
    );
  }

  Future _onCreate(Database db, int version) async {
    await db.execute('''
      CREATE TABLE $transactionsTable (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        amount REAL NOT NULL,
        type INTEGER NOT NULL, -- 0 = expense, 1 = income
        category TEXT NOT NULL,
        date TEXT NOT NULL
      )
    ''');

    await db.execute('''
      CREATE TABLE $budgetsTable (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT UNIQUE NOT NULL,
        amount REAL NOT NULL
      )
    ''');
  }

  // Transaction CRUD operations
  Future<int> insertTransaction(Map<String, dynamic> row) async {
    Database db = await instance.database;
    return await db.insert(transactionsTable, row);
  }

  Future<List<Map<String, dynamic>>> getTransactions() async {
    Database db = await instance.database;
    return await db.query(transactionsTable, orderBy: 'date DESC');
  }

  Future<int> updateTransaction(Map<String, dynamic> row) async {
    Database db = await instance.database;
    int id = row['id'];
    return await db.update(transactionsTable, row, where: 'id = ?', whereArgs: [id]);
  }

  Future<int> deleteTransaction(int id) async {
    Database db = await instance.database;
    return await db.delete(transactionsTable, where: 'id = ?', whereArgs: [id]);
  }

  // Budget CRUD operations
  Future<int> setBudget(Map<String, dynamic> row) async {
    Database db = await instance.database;
    return await db.insert(budgetsTable, row,
        conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<Map<String, double>> getBudgets() async {
    Database db = await instance.database;
    final List<Map<String, dynamic>> maps = await db.query(budgetsTable);
    return { for (var b in maps) b['category'] : b['amount'] };
  }
}
