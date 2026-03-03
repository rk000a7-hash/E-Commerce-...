import { useContext } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ShoppingCart, User, LogOut } from "lucide-react";
import { AuthContext } from "../context/AuthContext";
import { CartContext } from "../context/CartContext";

export default function Navbar() {
    const { user, logout } = useContext(AuthContext);
    const { cart } = useContext(CartContext);
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate("/login");
    };

    const cartItemCount = cart?.items?.reduce((total, item) => total + item.quantity, 0) || 0;

    return (
        <nav className="bg-white shadow-md sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16 items-center">
                    <Link to="/" className="text-2xl font-bold text-indigo-600">
                        PyShop
                    </Link>

                    <div className="flex items-center space-x-6">
                        <Link to="/products" className="text-gray-600 hover:text-indigo-600 font-medium">
                            Products
                        </Link>

                        <Link to="/cart" className="relative group text-gray-600 hover:text-indigo-600">
                            <ShoppingCart className="w-6 h-6" />
                            {cartItemCount > 0 && (
                                <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center">
                                    {cartItemCount}
                                </span>
                            )}
                        </Link>

                        {user ? (
                            <div className="flex items-center space-x-4">
                                <Link to="/dashboard" className="text-gray-600 hover:text-indigo-600 flex items-center">
                                    <User className="w-5 h-5 mr-1" />
                                    <span className="hidden sm:inline font-medium">{user.name}</span>
                                </Link>
                                <button
                                    onClick={handleLogout}
                                    className="text-gray-600 hover:text-red-500 flex items-center"
                                >
                                    <LogOut className="w-5 h-5" />
                                </button>
                            </div>
                        ) : (
                            <Link
                                to="/login"
                                className="bg-indigo-600 text-white px-4 py-2 rounded-md font-medium hover:bg-indigo-700 transition"
                            >
                                Login
                            </Link>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
}
