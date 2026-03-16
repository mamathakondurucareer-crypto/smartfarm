/**
 * Test user credentials for each role.
 * These map to users seeded by backend/seeds/seed_data.py.
 *
 * To recreate: python3 -m backend.seeds.seed_data
 */

const USERS = {
  admin: {
    username: "admin",
    password: "admin123",
    role: "admin",
    displayName: "Farm Administrator",
    email: "admin@smartfarm.in",
  },
  manager: {
    username: "manager",
    password: "manager123",
    role: "manager",
    displayName: "Ravi Kumar",
    email: "manager@smartfarm.in",
  },
  supervisor: {
    username: "supervisor1",
    password: "supervisor123",
    role: "supervisor",
    displayName: "Anil Supervisor",
    email: "supervisor1@smartfarm.in",
  },
  worker: {
    username: "worker1",
    password: "worker123",
    role: "worker",
    displayName: "Gopal Worker",
    email: "worker1@smartfarm.in",
  },
  viewer: {
    username: "viewer1",
    password: "viewer123",
    role: "viewer",
    displayName: "Sita Viewer",
    email: "viewer1@smartfarm.in",
  },
  store_manager: {
    username: "store_mgr",
    password: "store123",
    role: "store_manager",
    displayName: "Priya Store Manager",
    email: "store@smartfarm.in",
  },
  cashier: {
    username: "cashier1",
    password: "cashier123",
    role: "cashier",
    displayName: "Ramu Cashier",
    email: "cashier1@smartfarm.in",
  },
  packer: {
    username: "packer1",
    password: "packer123",
    role: "packer",
    displayName: "Krishna Packer",
    email: "packer1@smartfarm.in",
  },
  driver: {
    username: "driver1",
    password: "driver123",
    role: "driver",
    displayName: "Ramesh Driver",
    email: "driver1@smartfarm.in",
  },
  scanner: {
    username: "scanner1",
    password: "scanner123",
    role: "scanner",
    displayName: "Sunil Scanner",
    email: "scanner1@smartfarm.in",
  },
};

module.exports = { USERS };
