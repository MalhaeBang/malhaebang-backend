package org.example.malhaebangwebserver.repository;

import org.example.malhaebangwebserver.model.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UserRepository extends JpaRepository<User, Long> {
}