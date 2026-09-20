package com.acme.dao;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.Statement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class OrderDaoImpl implements OrderDao {

    private static final String DB_URL = "jdbc:mysql://localhost:3306/acmedb";

    @Override
    public Order findById(long orderId) {
        String sql = "SELECT * FROM orders WHERE id = " + orderId;
        try (Connection conn = DriverManager.getConnection(DB_URL, "root", "password");
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {

            if (rs.next()) {
                Order order = new Order();
                order.setId(rs.getLong("id"));
                order.setStatus(rs.getString("status"));
                return order;
            }
        } catch (SQLException e) {
            throw new RuntimeException("Failed to fetch order", e);
        }
        return null;
    }

    @Override
    public void update(Order order) {
        String sql = "UPDATE orders SET status = ? WHERE id = ?";
        try (Connection conn = DriverManager.getConnection(DB_URL, "root", "password");
             PreparedStatement ps = conn.prepareStatement(sql)) {

            ps.setString(1, order.getStatus());
            ps.setLong(2, order.getId());
            ps.executeUpdate();
        } catch (SQLException e) {
            throw new RuntimeException("Failed to update order", e);
        }
    }

    public boolean cancelOrderDirect(long orderId) {
        String sql = "UPDATE orders SET status = 'CANCELLED' WHERE id = " + orderId;
        try (Connection conn = DriverManager.getConnection(DB_URL, "root", "password");
             Statement stmt = conn.createStatement()) {

            int rowsAffected = stmt.executeUpdate(sql);
            return rowsAffected > 0;
        } catch (SQLException e) {
            throw new RuntimeException("Failed to cancel order", e);
        }
    }
}
