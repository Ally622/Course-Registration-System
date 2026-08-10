# Database Migrations

This directory contains all database migration scripts that were used during development to evolve the schema from initial version to the current production structure.

## Migration History

### 001_auth_flow.sql
**Purpose**: Enhanced authentication system
**Date**: Development Phase 1
**Changes**:
- Added password reset functionality
- Implemented session management
- Enhanced user roles and permissions

### 002_admission.sql  
**Purpose**: Admission workflow implementation
**Date**: Development Phase 2
**Changes**:
- Added KCSE information tables
- Implemented application management
- Added programme selection workflow

### 003_add_programme_to_units.sql
**Purpose**: Programme-Unit relationship establishment
**Date**: Development Phase 3
**Changes**:
- Added programme_id foreign key to units table
- Established clear programme-unit relationships
- Fixed unit assignment logic

### 004_add_duration_years.sql
**Purpose**: Programme duration configuration
**Date**: Development Phase 4
**Changes**:
- Added duration_years column to programmes table
- Set appropriate duration for different degree types
- Enhanced programme metadata

## Usage Notes

**⚠️ Important**: These migration files are for historical reference only. 

**For new installations**:
- Use `database/schema.sql` which contains the complete, final database structure
- Do NOT run these migration files on new installations

**For existing databases**:
- These migrations may be relevant if upgrading from an older version
- Apply migrations in numerical order
- Always backup your database before applying migrations

## Migration Best Practices

1. **Always backup** your database before applying any migration
2. **Test migrations** on a copy of production data first
3. **Apply in order** - migrations may depend on previous changes
4. **Verify results** after each migration
5. **Document changes** in commit messages and change logs

## Current Schema Version

The current production schema version includes all changes from these migrations. The final, complete schema is defined in `database/schema.sql`.